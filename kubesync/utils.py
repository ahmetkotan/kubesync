# Standard Library
import io
import random
import string
import tarfile
from typing import Optional
from pathlib import Path


def create_archive(file: str, archive_name=None) -> Optional[io.BytesIO]:
    stream = io.BytesIO()

    if archive_name is None:
        archive_name = Path(file).name

    with tarfile.TarFile(fileobj=stream, mode="w") as archive:
        if not Path(file).exists():
            return None
        archive.add(file, archive_name)

    stream.seek(0)
    return stream


def get_random_name() -> str:
    name = random.choices(string.ascii_lowercase + string.digits, k=10)
    return "".join(name)


def get_kubesync_directory() -> Path:
    home_directory = Path.home()
    kubesync_directory = home_directory.joinpath(".kubesync")
    if not kubesync_directory.exists():
        kubesync_directory.mkdir()

    return kubesync_directory
