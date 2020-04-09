# Standard Library
import os
from pathlib import Path

# First Party
from docker import DockerClient
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

    def move_object(self, src_path, is_directory) -> bool:
        archive = create_archive(src_path)
        if archive is None:
            return False

        abs_path = str(Path(self.sync.source_path))
        remote_abs_path = str(Path(self.sync.destination_path))

        relative_path = src_path.replace(abs_path + "/", "")
        dst_path = os.path.join(remote_abs_path, relative_path)
        if not is_directory:
            dst_path = str(Path(dst_path).parent)

        return self.container.put_archive(data=archive, path=dst_path)

    def delete_object(self, src_path, is_directory) -> str:
        command = ["/bin/rm"]
        if is_directory:
            command.append("-r")

        abs_path = str(Path(self.sync.source_path))
        remote_abs_path = str(Path(self.sync.destination_path))

        relative_path = src_path.replace(abs_path + "/", "")
        dst_path = os.path.join(remote_abs_path, relative_path)
        command.append(dst_path)

        return self.container.exec_run(command)
