import asyncio
import logging
import os
import pickle
from getpass import getpass
from pathlib import Path

import aiohttp
from platformdirs import user_cache_dir
from tqdm import tqdm

from earthcare_downloader import metadata
from earthcare_downloader.html_parser import HTMLParser

FILE_PATH = Path(__file__).resolve().parent
COOKIE_PATH = (
    Path(user_cache_dir("earthcare_downloader", ensure_exists=True)) / "cookies.pkl"
)


class BarConfig:
    def __init__(
        self, n_data: int, max_workers: int, disable_progress: bool | None
    ) -> None:
        self.disable_progress = disable_progress
        self.position_queue = self._init_position_queue(max_workers)
        self.total_amount = tqdm(
            total=0,
            desc="Total amount",
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
            disable=self.disable_progress,
            position=0,
        )
        self.overall = tqdm(
            total=n_data,
            desc="Total file progress",
            unit="file",
            disable=self.disable_progress,
            position=1,
        )
        self.lock = asyncio.Lock()

    def _init_position_queue(self, max_workers: int) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        for i in range(2, max_workers + 2):
            queue.put_nowait(i)
        return queue


async def download_overpass_data(
    lat: float,
    lon: float,
    distance: float,
    product: metadata.Prod,
    max_workers: int,
    output_path: Path,
) -> list[Path]:
    output_path.mkdir(parents=True, exist_ok=True)
    urls = await metadata.get_files(product, lat, lon, distance)
    logging.info(f"Found {len(urls)} files to download.")
    return await download_files(urls, output_path, max_workers) if urls else []


async def download_files(
    urls: list[str],
    output_path: Path,
    max_workers: int,
    disable_progress: bool | None = None,
) -> list[Path]:
    full_paths = []

    session = await _init_session(urls[0])
    semaphore = asyncio.Semaphore(max_workers)
    bar_config = BarConfig(len(urls), max_workers, disable_progress)

    async with session:
        tasks = []
        for url in urls:
            destination = output_path / url.split("/")[-1]
            full_paths.append(destination)
            task = asyncio.create_task(
                _download_with_retries(session, url, destination, semaphore, bar_config)
            )
            tasks.append(task)
        await asyncio.gather(*tasks)
        bar_config.overall.close()
        bar_config.overall.clear()
    return full_paths


async def _download_with_retries(
    session: aiohttp.ClientSession,
    url: str,
    destination: Path,
    semaphore: asyncio.Semaphore,
    bar_config: BarConfig,
) -> None:
    position = await bar_config.position_queue.get()
    try:
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                await _download_file(
                    session,
                    url,
                    destination,
                    semaphore,
                    bar_config,
                    position,
                )
                return
            except aiohttp.ClientError as e:
                logging.warning(f"Attempt {attempt} failed for {url}: {e}")
                if attempt == max_retries:
                    logging.error(f"Giving up on {url} after {max_retries} attempts.")
                    raise
                await asyncio.sleep(2**attempt)
    finally:
        bar_config.position_queue.put_nowait(position)


async def _download_file(
    session: aiohttp.ClientSession,
    url: str,
    destination: Path,
    semaphore: asyncio.Semaphore,
    bar_config: BarConfig,
    position: int,
) -> None:
    async with semaphore, session.get(url) as response:
        response.raise_for_status()
        bar = tqdm(
            desc=destination.name,
            total=response.content_length,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
            disable=bar_config.disable_progress,
            position=position,
            leave=False,
        )
        try:
            with destination.open("wb") as f:
                while chunk := await response.content.read(8192):
                    f.write(chunk)
                    bar.update(len(chunk))
                    bar_config.total_amount.update(len(chunk))
        finally:
            bar.close()
            bar.clear()
    bar_config.overall.update(1)


async def _init_session(test_url: str) -> aiohttp.ClientSession:
    session = aiohttp.ClientSession()
    if COOKIE_PATH.exists():
        with COOKIE_PATH.open("rb") as f:
            if not isinstance(session.cookie_jar, aiohttp.CookieJar):
                raise RuntimeError("Bad cookies!")
            session.cookie_jar._cookies = pickle.load(f)
    try:
        async with session.get(test_url) as res:
            if "login" in str(res.url).lower() or res.status in {401, 403}:
                logging.info("Session expired or not authenticated. Logging in...")
                await _authenticate_session(session, test_url)
                with COOKIE_PATH.open("wb") as f:
                    if not isinstance(session.cookie_jar, aiohttp.CookieJar):
                        raise RuntimeError("Bad cookies!")
                    pickle.dump(session.cookie_jar._cookies, f)
    except Exception:
        await session.close()
        raise
    return session


async def _authenticate_session(session: aiohttp.ClientSession, test_url: str) -> None:
    credentials = _get_credentials()
    async with session.get(test_url, auth=aiohttp.BasicAuth(*credentials)) as res:
        res.raise_for_status()
        text = await res.text()

    parser = HTMLParser(text)
    auth_url = parser.parse_url()
    payload = {
        "tocommonauth": "true",
        "username": credentials[0],
        "password": credentials[1],
        "sessionDataKey": parser.parse_session_key(),
    }

    async with session.post(auth_url, data=payload) as res:
        res.raise_for_status()
        text = await res.text()

    parser = HTMLParser(text)
    form_url = parser.parse_form_url()
    data = parser.parse_form_data()
    async with session.post(form_url, data=data) as res:
        res.raise_for_status()


def _get_credentials() -> tuple[str, str]:
    username = os.getenv("ESA_EO_USERNAME")
    password = os.getenv("ESA_EO_PASSWORD")
    if username is None or password is None:
        username = input("ESA EO username: ")
        password = getpass("ESA EO password: ")
    return username, password
