from abc import ABC, abstractmethod
from typing import Any


class RDBRepositoryGateway(ABC):
    @abstractmethod
    def get(self, element: int | dict[str, Any]) -> list[Any]:
        pass

    @abstractmethod
    def set(self, record: list[Any]) -> bool:
        pass

    @abstractmethod
    def is_exist(self, element: int | dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def get_new_id(self) -> int:
        pass

    @abstractmethod
    def initialize_table(self) -> None:
        pass
