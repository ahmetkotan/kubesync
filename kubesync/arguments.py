# Standard Library
import os
import sys

# Third Party
import click
import docker
from tabulate import tabulate
from minislite import MiniSLiteDb
from minislite.exceptions import AlreadyExistsError, RecordNotFoundError

# First Party
from kubesync.dock import DockerSync
from kubesync.kube import KubeManager
from kubesync.radar import Watcher
from kubesync.utils import read_archive, get_random_name, get_kubesync_directory
from kubesync.colors import print_red, print_green
from kubesync.models import Sync, WatcherStatus


@click.group()
def main():
    pass


@main.command()
@click.option("--selector", "-l", required=True)
@click.option("--container", "-c", required=True)
@click.option("--src", "-s", required=True)
@click.option("--dest", "-d", required=True)
@click.option("--name", "-n")
def create(selector, container, src, dest, name=None):
    if name is None:
        name = get_random_name()
    try:
        Sync.objects.create(
            selector=selector, container_name=container, source_path=src, destination_path=dest, name=name
        )
    except AlreadyExistsError:
        print_red("This watcher already exists.")


@main.command()
def get():
    syncs = Sync.objects.all()
    sync_table = []

    watcher = WatcherStatus.objects.first()
    watcher_status = watcher.status

    for s in syncs:
        status = s.get_status() if watcher_status else "not running"
        sync_table.append([s.id, s.name, s.selector, s.container_name, s.source_path, s.destination_path, status])

    headers = ["Id", "Name", "Selector", "Container", "Source Path", "Destination Path", "Status"]
    table = tabulate(sync_table, headers=headers)

    print(table)


@main.command()
def clean():
    Sync.objects.delete(i_am_sure=True)
    WatcherStatus.objects.delete(i_am_sure=True)


@main.command()
@click.argument("sync_id_or_name", required=True)
def delete(sync_id_or_name):
    kwargs = {"name": sync_id_or_name}
    if sync_id_or_name.isdigit():
        kwargs = {"id": sync_id_or_name}
    try:
        sync_obj = Sync.objects.get(**kwargs)
        sync_obj.delete()
    except RecordNotFoundError:
        print_red("This watcher does not exists.")


@main.command()
@click.option("--selector", "-l", required=True)
@click.option("--container", "-c", required=True)
@click.option("--src", "-s", required=True)
@click.option("--dest", "-d", required=True)
def sync(selector, container, src, dest):
    kube = KubeManager()
    container = kube.get_container(selector=selector, container_name=container)
    if container:
        temp_sync = Sync()
        temp_sync.source_path = src
        temp_sync.destination_path = dest
        temp_sync.container_id = container.container_id

        docker_client = docker.from_env()
        DockerSync(docker_client=docker_client, sync=temp_sync, standalone=True)
    else:
        print_red(f"{selector}::{container} not found in kube pods.")
        sys.exit(1)


@main.command()
@click.option("--selector", "-l", required=True)
@click.option("--container", "-c", required=True)
@click.option("--src", "-s", required=True)
@click.option("--dest", "-d", required=True)
def clone(selector, container, src, dest):
    kube = KubeManager()
    container = kube.get_container(selector=selector, container_name=container)
    if container:
        docker_client = docker.from_env()
        read_archive(docker_client, container.container_id, dest, src, extract=True)
    else:
        print_red(f"{selector}::{container} not found in kube pods.")
        sys.exit(1)


@main.command()
@click.option("--pid-file")
def watch(pid_file=None):
    print_green("Start watching.")

    if pid_file is None:
        kubesync_directory = get_kubesync_directory()
        pid_file = str(kubesync_directory.joinpath("kubesync.pid"))

    with open(pid_file, "w") as pid:
        pid.write("%s" % os.getpid())
    print_green("PID saved.")

    watcher = Watcher()
    watcher.run()


def execute():
    kubesync_directory = get_kubesync_directory()
    database_path = kubesync_directory.joinpath("kubesync.db")
    database = MiniSLiteDb(str(database_path))
    database.add_model(Sync)
    database.add_model(WatcherStatus)

    if not WatcherStatus.objects.all():
        WatcherStatus.objects.create(status=False)

    main()
