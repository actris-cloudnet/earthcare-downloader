import asyncio
import logging
import os
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import aiohttp
from platformdirs import user_cache_dir
from tqdm import tqdm

from earthcare_downloader import metadata

from .params import File, SearchParams, TaskParams

logger = logging.getLogger(__name__)

TOKEN_URL = "https://iam.maap.eo.esa.int/realms/esa-maap/protocol/openid-connect/token"
TOKEN_PATH = Path(user_cache_dir("earthcare_downloader", ensure_exists=True)) / "token"


@dataclass
class AuthSession:
    """Holds an aiohttp session with automatic token refresh on 401."""

    session: aiohttp.ClientSession
    offline_token: str
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    _current_token: str = ""

    async def refresh(self, failed_token: str) -> None:
        """Re-exchange the offline token if it hasn't been refreshed already."""
        async with self._lock:
            if self._current_token != failed_token:
                return  # Another task already refreshed
            self._current_token = await _exchange_token(self.offline_token)
            self.session.headers["Authorization"] = f"Bearer {self._current_token}"


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
    token: str | None = None,
) -> list[Path]:
    files = await metadata.get_files(search_params)

    if not files:
        logger.info("No files found.")
        return []

    files_sorted = sorted(files, key=lambda f: f.frame_start_time)
    header = (
        f"{'PRODUCT':<14} {'BASELINE':<10} {'ORBIT':<7} "
        f"{'FRAME START TIME':<20} {'PROCESSING TIME':<19}"
    )
    logger.info(header)
    logger.info("-" * len(header))

    for f in files_sorted:
        orbit_str = str(f.orbit) if f.orbit is not None else ""
        proc_str = f"{f.processing_time:%Y-%m-%d %H:%M:%S}" if f.processing_time else ""
        logger.info(
            f"{f.product:<14} {f.baseline:<10} {orbit_str:<7} "
            f"{f.frame_start_time:%Y-%m-%d %H:%M:%S}  "
            f"{proc_str}"
        )

    if not task_params.yes:
        confirmed = input(
            f"Proceed with downloading {len(files)} files? [y/n]: "
        ).strip().lower() in ("y", "yes")
    else:
        confirmed = True

    if not confirmed:
        return []

    return await download_files(files, task_params, token=token)


@dataclass
class DlParams:
    url: str
    destination: Path
    auth_session: AuthSession
    semaphore: asyncio.Semaphore
    bar_config: BarConfig


async def download_files(
    files: list[File],
    task_params: TaskParams,
    token: str | None = None,
) -> list[Path]:
    _make_folders(task_params, files)

    to_download = _files_to_download(files, task_params)
    if not to_download:
        return []

    auth_session = await _init_session(token)
    semaphore = asyncio.Semaphore(task_params.max_workers)
    bar_config = BarConfig(len(to_download), task_params)

    async with auth_session.session:
        tasks = [
            asyncio.create_task(
                _download_with_retries(
                    DlParams(
                        url=url,
                        destination=dest,
                        auth_session=auth_session,
                        semaphore=semaphore,
                        bar_config=bar_config,
                    )
                )
            )
            for url, dest in to_download
        ]
        if task_params.quiet is True:
            print(f"Downloading {len(to_download)} files...", end="", flush=True)
        full_paths = await asyncio.gather(*tasks)
        if task_params.quiet is True:
            print(" done.", flush=True)
        bar_config.overall.close()
        bar_config.overall.clear()

    return [path for paths in full_paths for path in paths]


def _files_to_download(
    files: list[File], task_params: TaskParams
) -> list[tuple[str, Path]]:
    """Return (url, destination) pairs for files that need downloading."""
    result: list[tuple[str, Path]] = []
    for file in files:
        root = task_params.output_path
        if task_params.by_product:
            root /= file.product

        destination = root / Path(file.filename)

        if not task_params.force and destination.exists():
            continue

        result.append((file.url, destination))
    return result


async def _download_with_retries(
    params: DlParams,
) -> list[Path]:
    position = await params.bar_config.position_queue.get()
    try:
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                await _download_file(
                    params,
                    position,
                )
                if params.destination.suffix.lower() == ".zip":
                    with zipfile.ZipFile(params.destination) as zf:
                        extracted = [
                            Path(zf.extract(f, params.destination.parent))
                            for f in zf.filelist
                        ]
                    params.destination.unlink()
                    return extracted
                return [params.destination]
            except aiohttp.ClientError as e:
                logger.warning(f"Attempt {attempt} failed for {params.url}: {e}")
                if attempt == max_retries:
                    logger.error(
                        f"Giving up on {params.url} after {max_retries} attempts."
                    )
                    raise
                await asyncio.sleep(2**attempt)
    finally:
        params.bar_config.position_queue.put_nowait(position)
    raise AssertionError


async def _download_file(
    params: DlParams,
    position: int,
) -> None:
    async with params.semaphore:
        response = await params.auth_session.session.get(params.url)
        if response.status == 401:
            failed_token = params.auth_session._current_token
            response.release()
            logger.info("Access token expired, refreshing...")
            await params.auth_session.refresh(failed_token)
            response = await params.auth_session.session.get(params.url)
        try:
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
            part_path = params.destination.with_suffix(
                params.destination.suffix + ".part"
            )
            try:
                with part_path.open("wb") as f:
                    while chunk := await response.content.read(65536):
                        f.write(chunk)
                        bar.update(len(chunk))
                        params.bar_config.total_amount.update(len(chunk))
                part_path.rename(params.destination)
            except BaseException:
                part_path.unlink(missing_ok=True)
                raise
            finally:
                bar.close()
                bar.clear()
        finally:
            response.release()
    params.bar_config.overall.update(1)


async def _init_session(token: str | None) -> AuthSession:
    """Create an authenticated session using OIDC token exchange."""
    offline_token = _get_offline_token(token)
    access_token = await _exchange_token(offline_token)
    session = aiohttp.ClientSession(headers={"Authorization": f"Bearer {access_token}"})
    return AuthSession(
        session=session, offline_token=offline_token, _current_token=access_token
    )


async def _exchange_token(offline_token: str) -> str:
    """Exchange an offline token for a short-lived access token."""
    async with (
        aiohttp.ClientSession() as session,
        session.post(
            TOKEN_URL,
            data={
                "client_id": "offline-token",
                "client_secret": "p1eL7uonXs6MDxtGbgKdPVRAmnGxHpVE",
                "grant_type": "refresh_token",
                "refresh_token": offline_token,
            },
        ) as response,
    ):
        response.raise_for_status()
        data = await response.json()
        return data["access_token"]


def _get_offline_token(token: str | None) -> str:
    """Get offline token from argument, env var, file, or user prompt."""
    if token:
        return token

    env_token = os.getenv("MAAP_TOKEN")
    if env_token:
        return env_token

    if TOKEN_PATH.exists():
        return TOKEN_PATH.read_text().strip()

    logger.info(
        "No MAAP token found. Get a 90-day offline token from:\n"
        "https://portal.maap.eo.esa.int/ini/services/auth/token/90dToken.php"
    )
    token_input = input("Paste your MAAP token: ").strip()
    TOKEN_PATH.write_text(token_input)
    TOKEN_PATH.chmod(0o600)
    return token_input


def _make_folders(task_params: TaskParams, files: list[File]) -> None:
    task_params.output_path.mkdir(parents=True, exist_ok=True)
    products = {file.product for file in files}
    if task_params.by_product:
        for product in products:
            (task_params.output_path / product).mkdir(exist_ok=True)
