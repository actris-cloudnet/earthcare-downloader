import asyncio
import logging
import os
import zipfile
from contextlib import suppress
from dataclasses import dataclass
from getpass import getpass
from pathlib import Path

import aiohttp
from platformdirs import user_cache_dir
from tqdm import tqdm

from earthcare_downloader import metadata
from earthcare_downloader.html_parser import HTMLParser

from .params import File, SearchParams, TaskParams

FILE_PATH = Path(__file__).resolve().parent
COOKIE_PATH = (
    Path(user_cache_dir("earthcare_downloader", ensure_exists=True)) / "cookies.pkl"
)


class BarConfig:
    def __init__(self, n_data: int, task_params: TaskParams) -> None:
        self.quiet = task_params.quiet
        self.position_queue = self._init_position_queue(task_params.max_workers)
        self.total_amount = tqdm(
            total=0,
            desc="Total amount",
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
            disable=self.quiet,
            position=0,
            leave=False,
        )
        self.overall = tqdm(
            total=n_data,
            desc="Total file progress",
            unit="file",
            disable=self.quiet,
            position=1,
            colour="green",
            leave=False,
        )
        self.lock = asyncio.Lock()

    def _init_position_queue(self, max_workers: int) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        for i in range(2, max_workers + 2):
            queue.put_nowait(i)
        return queue


async def search_and_download(
    search_params: SearchParams,
    task_params: TaskParams,
) -> list[Path]:
    files = await metadata.get_files(search_params)

    if not files:
        logging.info("No files found.")
        return []

    if task_params.show:
        for file in files:
            logging.info(file.url)

    if not task_params.no_prompt:
        confirmed = input(
            f"Proceed with downloading {len(files)} files? [y/n]: "
        ).strip().lower() in ("y", "yes")
    else:
        confirmed = True

    if not confirmed:
        return []

    return await download_files(files, task_params)


@dataclass
class DlParams:
    url: str
    destination: Path
    session: aiohttp.ClientSession
    semaphore: asyncio.Semaphore
    bar_config: BarConfig
    unzip: bool


async def download_files(
    files: list[File],
    task_params: TaskParams,
    credentials: tuple[str, str] | None = None,
) -> list[Path]:
    _make_folders(task_params, files)

    session = await _init_session(files, credentials)
    semaphore = asyncio.Semaphore(task_params.max_workers)
    bar_config = BarConfig(len(files), task_params)

    async with session:
        tasks = []
        for file in files:
            root = task_params.output_path
            if task_params.by_product:
                root /= file.product

            destination = root / Path(file.filename)

            dl_stuff = DlParams(
                url=file.url,
                destination=destination,
                session=session,
                semaphore=semaphore,
                bar_config=bar_config,
                unzip=task_params.unzip,
            )
            task = asyncio.create_task(_download_with_retries(dl_stuff))
            tasks.append(task)
        full_paths = await asyncio.gather(*tasks)
        bar_config.overall.close()
        bar_config.overall.clear()
    return full_paths


async def _download_with_retries(
    params: DlParams,
) -> Path:
    position = await params.bar_config.position_queue.get()
    try:
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                await _download_file(
                    params,
                    position,
                )
                if params.unzip and params.destination.suffix.lower() == ".zip":
                    with zipfile.ZipFile(params.destination, "r") as zip_ref:
                        for file_info in zip_ref.filelist:
                            if file_info.filename.lower().endswith(".h5"):
                                filename = zip_ref.extract(
                                    file_info, params.destination.parent
                                )
                    params.destination.unlink()
                return Path(filename) if params.unzip else params.destination
            except aiohttp.ClientError as e:
                logging.warning(f"Attempt {attempt} failed for {params.url}: {e}")
                if attempt == max_retries:
                    logging.error(
                        f"Giving up on {params.url} after {max_retries} attempts."
                    )
                    raise
                await asyncio.sleep(2**attempt)
    finally:
        params.bar_config.position_queue.put_nowait(position)
    raise RuntimeError("Unreachable code reached.")


async def _download_file(
    params: DlParams,
    position: int,
) -> None:
    async with params.semaphore, params.session.get(params.url) as response:
        response.raise_for_status()
        bar = tqdm(
            desc=params.destination.name,
            total=response.content_length,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
            disable=params.bar_config.quiet,
            position=position,
            leave=False,
            colour="cyan",
        )
        try:
            with params.destination.open("wb") as f:
                while chunk := await response.content.read(8192):
                    f.write(chunk)
                    bar.update(len(chunk))
                    params.bar_config.total_amount.update(len(chunk))
        finally:
            bar.close()
            bar.clear()
    params.bar_config.overall.update(1)


async def _init_session(
    files: list[File], credentials: tuple[str, str] | None
) -> aiohttp.ClientSession:
    jar = aiohttp.CookieJar()
    if COOKIE_PATH.exists():
        jar.load(COOKIE_PATH)
    session = aiohttp.ClientSession(cookie_jar=jar)
    servers = {file.server for file in files}
    for server in servers:
        try:
            async with session.get(server) as res:
                body = await res.text()
                if "logout" not in body.lower():
                    logging.info(f"Logging in to {server}")
                    login_url = f"{server}/access/login"
                    await _authenticate_session(session, login_url, credentials)
                    jar.save(COOKIE_PATH)
        except Exception:
            await session.close()
            raise
    return session


async def _authenticate_session(
    session: aiohttp.ClientSession, login_url: str, credentials: tuple[str, str] | None
) -> None:
    credentials = credentials or _get_credentials()
    async with session.get(login_url, auth=aiohttp.BasicAuth(*credentials)) as res:
        res.raise_for_status()
        text = await res.text()

    parser = HTMLParser(text)
    try:
        auth_url = parser.parse_url()
    except ValueError:
        auth_url = login_url
    payload = {
        "tocommonauth": "true",
        "username": credentials[0],
        "password": credentials[1],
    }
    with suppress(ValueError):
        payload["sessionDataKey"] = parser.parse_session_key()

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


def _make_folders(task_params: TaskParams, files: list[File]) -> None:
    task_params.output_path.mkdir(parents=True, exist_ok=True)
    products = {file.product for file in files}
    if task_params.by_product:
        for product in products:
            (task_params.output_path / product).mkdir(exist_ok=True)
