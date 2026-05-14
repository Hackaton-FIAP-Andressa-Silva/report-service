from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.report import Report


class ReportRepository(ABC):
    @abstractmethod
    async def save(self, report: Report) -> Report:
        ...

    @abstractmethod
    async def find_by_upload_id(self, upload_id: str) -> Optional[Report]:
        ...
