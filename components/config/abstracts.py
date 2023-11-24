from abc import ABC, abstractmethod
from typing import List, Dict


class SecretsHolder(ABC):
    @abstractmethod
    def get_secrets(self, secrets_names: List[str]) -> Dict[str, str]:
        pass
