# Standard Library
from pathlib import Path

# First Party
from docker import DockerClient, errors
from kubesync.utils import create_archive
from kubesync.models import Sync


class DockerSync:
    def __init__(self, docker_client: DockerClient, sync: Sync, standalone=False):
        self.sync = sync
        self.client = docker_client
        self.container_id = sync.container_id

        self.container = self.client.containers.get(self.get_short_id())

        remote_app_directory_name = Path(self.sync.destination_path).name
        remote_parent_directory = str(Path(self.sync.destination_path).parent)

        if not standalone:
            self.sync.synced = 0
            self.sync.save()

        archive = create_archive(self.sync.source_path, remote_app_directory_name)
        if archive:
            self.container.put_archive(data=archive, path=remote_parent_directory)

        if not standalone:
            self.sync.synced = 1
            self.sync.save()

    def get_short_id(self) -> str:
        container_id = self.container_id.replace("docker://", "")
        container_id = container_id[:10]
        return container_id

    def move_object(self, source) -> bool:
        archive = create_archive(source)
        if archive is None:
            return False

        abs_path = Path(self.sync.source_path)
        remote_abs_path = Path(self.sync.destination_path)
        src_path = Path(source)

        relative_path = src_path.relative_to(abs_path)
        dst_path = remote_abs_path.joinpath(relative_path).parent

        try:
            return self.container.put_archive(data=archive, path=str(dst_path))
        except errors.NotFound:
            return False

    def delete_object(self, source, is_directory) -> str:
        command = ["/bin/rm"]
        if is_directory:
            command.append("-r")

        abs_path = Path(self.sync.source_path)
        remote_abs_path = Path(self.sync.destination_path)
        src_path = Path(source)

        relative_path = src_path.relative_to(abs_path)
        dst_path = remote_abs_path.joinpath(relative_path)
        command.append(str(dst_path))

        return self.container.exec_run(command)
