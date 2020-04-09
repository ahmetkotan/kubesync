# Third Party
# First Party
from minislite import DatabaseField, MiniSLiteModel


class Sync(MiniSLiteModel):
    name = DatabaseField(field_type=str)
    selector = DatabaseField(field_type=str)
    container_name = DatabaseField(field_type=str)
    source_path = DatabaseField(field_type=str)
    destination_path = DatabaseField(field_type=str)
    container_id = DatabaseField(field_type=str, not_null=False)
    connected = DatabaseField(field_type=bool, default=False)
    synced = DatabaseField(field_type=bool, default=False)

    unique_together = ["container_name", "selector"]

    def get_status(self):
        if self.connected:
            if not self.synced:
                return "reloading"
            return "watching"

        return "not connected"


class WatcherStatus(MiniSLiteModel):
    status = DatabaseField(field_type=bool, default=0)
