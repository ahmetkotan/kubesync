# Standard Library
import io
import random
import string
import tarfile
from typing import List, Tuple, Optional
from pathlib import Path

# Third Party
from docker import DockerClient


def is_path_ignored(path: Path) -> bool:
    from kubesync.arguments import KUBESYNC_IGNORE_PATTERNS

    for ignore in KUBESYNC_IGNORE_PATTERNS:
        if path.match(ignore):
            return True

        if True in [i.match(ignore) for i in path.parents]:
            return True

    return False


def tar_add_ignore_files(file: tarfile.TarInfo):
    path = Path(file.path)  # type: ignore
    if is_path_ignored(path):
        return None
    return file


def tar_extract_ignore_files(members: List[tarfile.TarInfo]):
    for file in members:
        path = Path(file.path)  # type: ignore
        if not is_path_ignored(path):
            yield file


def create_archive(file: str, archive_name=None) -> Tuple[Optional[io.BytesIO], Optional[tarfile.TarFile]]:
    stream = io.BytesIO()

    if archive_name is None:
        archive_name = Path(file).name

    if not Path(file).exists():
        return None, None

    archive = tarfile.TarFile(fileobj=stream, mode="w")
    archive.add(file, archive_name, filter=tar_add_ignore_files)

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
        tar_archive.extractall(str(destination_path), members=tar_extract_ignore_files(tar_archive.getmembers()))

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


def load_ignore_patterns(source: str):
    from kubesync.arguments import KUBESYNC_IGNORE_PATTERNS

    source_path = Path(source)
    ignore_file_path = source_path.joinpath(".kubesyncignore")
    if ignore_file_path.exists():
        ignore_lines = open(ignore_file_path).readlines()
        ignore_patterns = []
        for line in ignore_lines:
            line = line.strip()
            if line:
                ignore_patterns.append(line)
        KUBESYNC_IGNORE_PATTERNS.extend(ignore_patterns)
