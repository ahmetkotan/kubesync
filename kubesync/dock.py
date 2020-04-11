# Standard Library
from pathlib import Path

# Third Party
from docker import DockerClient, errors

# First Party
from kubesync.utils import read_archive, create_archive, get_container_short_id
from kubesync.models import Sync


class DockerSync:
    def __init__(self, docker_client: DockerClient, sync: Sync, standalone=False):
        self.sync = sync
        self.client = docker_client
        self.container = self.client.containers.get(get_container_short_id(sync.container_id))

        remote_app_directory_name = Path(self.sync.destination_path).name
        remote_parent_directory = str(Path(self.sync.destination_path).parent)

        if not standalone:
            self.sync.synced = 0
            self.sync.save()

        stream, archive = create_archive(self.sync.source_path, remote_app_directory_name)
        old_archive = read_archive(self.client, sync.container_id, sync.destination_path, sync.source_path)

        if old_archive and archive:
            remote_file_list = set(old_archive.getnames())
            host_file_list = set(archive.getnames())
            files_diff = remote_file_list.difference(host_file_list)
            for file in files_diff:
                member = old_archive.getmember(file)
                self.delete_object(member.name, member.isdir(), relative_path=remote_app_directory_name)

        if stream:
            self.container.put_archive(data=stream, path=remote_parent_directory)

        if not standalone:
            self.sync.synced = 1
            self.sync.save()

    def move_object(self, source) -> bool:
        stream, _ = create_archive(source)
        if stream is None:
            return False

        abs_path = Path(self.sync.source_path)
        remote_abs_path = Path(self.sync.destination_path)
        src_path = Path(source)

        relative_path = src_path.relative_to(abs_path)
        dst_path = remote_abs_path.joinpath(relative_path).parent

        try:
            return self.container.put_archive(data=stream, path=str(dst_path))
        except errors.NotFound:
            return False

    def delete_object(self, source, is_directory, relative_path=None) -> str:
        command = ["/bin/rm"]
        if is_directory:
            command.append("-r")

        if relative_path:
            abs_path = Path(relative_path)
        else:
            abs_path = Path(self.sync.source_path)
        remote_abs_path = Path(self.sync.destination_path)
        src_path = Path(source)

        relative_path = src_path.relative_to(abs_path)
        dst_path = remote_abs_path.joinpath(relative_path)
        command.append(str(dst_path))

        return self.container.exec_run(command)
