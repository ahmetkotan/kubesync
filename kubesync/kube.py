# Standard Library
import time
from typing import Optional

# Third Party
from kubernetes import client, config
from kubernetes.client import V1ContainerStatus


class KubeManager:
    def __init__(self) -> None:
        config.load_kube_config()
        self.core_api = client.CoreV1Api()

    def get_container(self, selector, container_name) -> Optional[V1ContainerStatus]:
        items = self.core_api.list_pod_for_all_namespaces(label_selector=selector).items
        if items:
            pod = items[0]

            for container in pod.status.container_statuses:
                if container.name == container_name:
                    if container.ready:
                        return container
                    time.sleep(1)
                    return self.get_container(selector, container_name)

        return None
