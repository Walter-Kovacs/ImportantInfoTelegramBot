import json
import logging
import traceback
from typing import Dict, List, Any, Optional, Set, Union, Tuple
from attrs import define, field
from components.configsecretholders.jsonfile import JSONFileSH
from components.config.abstracts import SecretsHolder

logger = logging.getLogger('config')

class SecretsReplaceException(Exception):
    pass

class SetValueByPathException(Exception):
    pass

def _set_value_by_path(
    current_node: Union[dict, list],
    path: List[Union[str,int]],
    value: Any,
):
    """
    Recursive function to set <value> into some certain place of <current_node>
    The place is described by <path> array like this one ["key1", 2, 0, 1]
    {
        "key1": [
            ..., # 0
            ..., # 1
            {    # 2
                0: [..., value], # numeric dict keys is valid
                100: ...
            },
            ... # 3
        ]
    }
    """
    if len(path) == 0:
        # just in case
        return

    next_key = path[0]

    if len(path) == 1:
        # it's a final key or index
        if isinstance(next_key, str):
            # it's surely key, so node should be a dict, check this fact
            if not isinstance(next_key, dict):
                raise SetValueByPathException(
                    f'Failed to set value into string key "{path[0]}" for node ({current_node}), '+
                    'cause of the last one is not dictionary',
                )
            current_node[next_key] = value
            return

        # here it's an index or number key, both variant are possible
        current_node[next_key] = value
        return

    # get next node by next_key
    next_node = current_node
    if isinstance(next_key, str):
        # it's surely key, so node should be a dict, check this fact
        if not isinstance(next_key, dict):
            raise SetValueByPathException(
                f'Failed to set value into string key "{path[0]}" for node ({current_node}), '+
                'cause of the last one is not dictionary',
            )
        next_node = current_node[next_key]
    else:
        # here it's an index or number key, both variant are possible
        next_node = current_node[next_key]

    _set_value_by_path(next_node, path[1:], value)

SECRET_PREFIX = 'SECRET:'

@define
class Secret:
    name_in_holder: str
    path_in_data: List[Union[str, int]]
    value: Optional[Any] = field(default=None)


class Config:
    data: Dict = {}

    @staticmethod
    def _lookup_secrets_next_layer(node: Union[Dict, List], current_path: List[Union[str, int]]) -> List[Secret]:
        secrets: List[Secret] = []
        if isinstance(node, dict):
            for k, subnode in node.items():
                secrets += Config._lookup_secrets_next_layer(subnode, current_path + [k])
        elif isinstance(node, list):
            for idx, subnode in enumerate(node):
                secrets += Config._lookup_secrets_next_layer(subnode, current_path + [idx])
        elif isinstance(node, str) and node.startswith(SECRET_PREFIX):
            secrets = [
                Secret(
                    name_in_holder = node[len(SECRET_PREFIX):],
                    path_in_data = current_path,
                )
            ]

        return secrets

    @classmethod
    def _search_for_secrets(cls) -> List[Secret]:
        return Config._lookup_secrets_next_layer(cls.data, [])

    @classmethod
    def _load_secrets_holder_from_config(cls) -> SecretsHolder:
        '''
        Searchs the config of certain secrets holder in the common config
        Expects that common config is already loaded into cls.data dictionary

        the key "type" should present into this dict
        Other fields depend on the value of the key "type"
        and provide the params of ceirtain secret holder of type "type"
        '''
        secret_holder_conf = cls.data.get('secrets_holder', None)
        if secret_holder_conf is None:
            raise SecretsReplaceException('Failed to found secret_holder config into common config '+
                        'the config is expected to be placed into "secret_holder" config object')

        holder_type = secret_holder_conf.get('type', '')
        if holder_type == '':
            raise SecretsReplaceException('Invalid secret holder config format, "type" is missing')
        if holder_type == 'jsonfile':
            filepath = secret_holder_conf.get("filepath", "")
            if filepath == "":
                raise SecretsReplaceException('Invalid format of "jsonfile" secret holder config: "filepath" key is missing')
            try:
                secret_holder = JSONFileSH(filepath)
            except Exception as e:
                raise SecretsReplaceException('Failed to init jsonfile secret holder: {e}')
        else:
            raise SecretsReplaceException(f'Unknown type of secret holder requested in config: {holder_type}; ' +
                                          'config types suppoerted: "jsonfile"')
        return secret_holder


    @classmethod
    def _check_dupls_in_secret_names(
        cls,
        unresolved_secrets: List[Secret],
    ) -> Tuple[List[str], Optional[List[str]]]:
        unique_secrets: Set[str]  = set()
        dupls: List[str] = []
        for secret in unresolved_secrets:
            if secret.name_in_holder in unique_secrets:
                dupls.append(secret.name_in_holder)
            else:
                unique_secrets.add(secret.name_in_holder)

        return ([], dupls) if len(dupls) != 0 else (list(unique_secrets), None)

    @classmethod
    def _resolve_secrets(cls, secrets: List[Secret]) -> List[Secret]:
        """
        Detect what secrets_holder to use from config
        Load it
        Validate incoming secrets with common checks
        Resolve requested secrets into their values using secrets_holder
        """
        secrets_holder = cls._load_secrets_holder_from_config()

        unique_secret_names, dupls = cls._check_dupls_in_secret_names(secrets)
        if dupls is not None:
            raise SecretsReplaceException(f'Failed to resolve secrets in config, duplications found: {dupls}')

        try:
            resolved_secret_names = secrets_holder.get_secrets(unique_secret_names)
        except Exception as e:
            raise SecretsReplaceException(
                f'Failed to resolve secret in config; secrets_holder ({type(secrets_holder)}) exception: {e}',
            )

        for secret in secrets:
            secret.value = resolved_secret_names[secret.name_in_holder]

        return secrets

    @classmethod
    def _replace_secrets(cls, secrets: List[Secret]):
        """
        Replace resolved secrets in class dictionary "data"
        """
        for secret in secrets:
            _set_value_by_path(cls.data, secret.path_in_data, secret.value)

    @classmethod
    def _set_class_data(cls, d: Dict):
        """
        Internal method to use in tests
        """
        cls.data = d

    @classmethod
    def read_from_file(cls, config_path: str) -> bool:
        with open(config_path, 'r') as config_file:
            cls.data = json.load(config_file)

        logger.info('Config file red successfully')
        logger.info('Searching for secrets placeholders')
        # deep dive into self.data searching string values with SECRET: prefix
        secrets: List[Secret] = cls._search_for_secrets()

        if len(secrets) != 0:
            try:
                logger.info('Resolving secrets')
                secrets = cls._resolve_secrets(secrets)
                logger.info('Replaceing secrets placeholders')
                cls._replace_secrets(secrets)
            except SecretsReplaceException as e:
                logger.error(f'Failed to replace secret values of config {traceback.format_exc()}')
                return False
            except Exception as e:
                logger.error(f"Caught unknown exception during loading the config {e}")
                return False
        else:
            logger.info('Secrets not found in config, so loaded config already prepared')
        return True



config = Config()
