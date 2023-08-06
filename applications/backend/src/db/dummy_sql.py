from typing import Any

from src.adapter.rdb_repository_gateway import RDBRepositoryGateway


class DummySQL(RDBRepositoryGateway):
    def __init__(
        self, table_name: str, pk: list[str], fk: dict[str, dict[str, str]]
    ) -> None:
        pass

    def get(self, element: int | dict[str, Any]) -> list[Any]:
        return ["dummy_data"]

    def set(self, record: list[Any]) -> bool:
        return True

    def is_exist(self, element: int | dict[str, Any]) -> bool:
        return True

    def get_new_id(self) -> int:
        return 1

    def initialize_table(self) -> None:
        pass
