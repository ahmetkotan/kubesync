# Standard Library
import io
import random
import string
import tarfile
from typing import Tuple, Optional
from pathlib import Path

# Third Party
from docker import DockerClient


def create_archive(file: str, archive_name=None) -> Tuple[Optional[io.BytesIO], Optional[tarfile.TarFile]]:
    stream = io.BytesIO()

    if archive_name is None:
        archive_name = Path(file).name

    if not Path(file).exists():
        return None, None

    archive = tarfile.TarFile(fileobj=stream, mode="w")
    archive.add(file, archive_name)

    stream.seek(0)
    return stream, archive


def read_archive(
    client: DockerClient, container_addr: str, container_path: str, host_path: str, extract: bool = False
) -> tarfile.TarFile:

    source_path = Path(container_path)
    destination_path = Path(host_path).parent

    container_id = get_container_short_id(container_addr)
    container = client.containers.get(container_id)

    archive, _ = container.get_archive(source_path)
    stream = io.BytesIO()
    stream.write(b"".join([i for i in archive]))
    stream.seek(0)

    tar_archive = tarfile.TarFile(fileobj=stream)
    if extract:
        tar_archive.extractall(str(destination_path))

    return tar_archive


def get_container_short_id(container_addr: str):
    container_id = container_addr.replace("docker://", "")
    container_id = container_id[:10]
    return container_id


def get_random_name() -> str:
    name = random.choices(string.ascii_lowercase + string.digits, k=10)
    return "".join(name)


def get_kubesync_directory() -> Path:
    home_directory = Path.home()
    kubesync_directory = home_directory.joinpath(".kubesync")
    if not kubesync_directory.exists():
        kubesync_directory.mkdir()

    return kubesync_directory
