from abc import ABC, abstractmethod

from src.models.admin import SystemSettings


class SettingsRepositoryInterface(ABC):
    @abstractmethod
    async def get(self) -> SystemSettings: ...

    @abstractmethod
    async def update(self, settings: SystemSettings) -> SystemSettings: ...
