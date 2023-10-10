from typing import List, Dict
from components.config.abstracts import SecretsHolder

class JSONFileSH(SecretsHolder):
    _secrets_to_replace: Dict[str, str]

    def __init__(self, filepath: str) -> None:
        self._secrets_to_replace = {}
        self._read_secrets_from_file(filepath)

    def _read_secrets_from_file(self, filepath: str):
        pass

    def get_secrets(self, secrets_names: List[str]) -> Dict[str, str]:
       return {}
