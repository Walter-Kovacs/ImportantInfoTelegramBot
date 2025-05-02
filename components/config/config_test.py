from typing import Dict, List, Optional
from unittest.mock import patch

import pytest
from attrs import define, field

from components.config.abstracts import SecretsHolder
from components.config.config import (SECRET_PREFIX, Config, Secret,
                                      SecretsReplaceException,
                                      SetValueByPathException, config)


class ConfigInternalsTestException(Exception):
    pass

@define
class SecretsHolderStub(SecretsHolder):
    raise_error: Optional[bool] = field(default=False)

    def get_secrets(self, secrets_names: List[str]) -> Dict[str,str]:
        if self.raise_error:
            raise Exception('test exception')
        return {name: name + "_secret_value" for name in secrets_names}


class TestConfigInternals:
    def sort_secrets(self, secrets):
        secrets.sort(key=lambda secret: '.'.join([str(item) for item in secret.path_in_data]))

    def test_search_for_secrets(self):
        # TEST PREPARATION
        # set test data dict
        config._set_class_data({
            "layer1_key1": "not_secret_value",
            "layer1_key2": {  # check diving into dict from dict. First dict is the main node
                "layer2_key1": "not_secret_value",
                "layer2_key2": SECRET_PREFIX + "layer2_name_of_secret",
            },
            "layer1_key3": [  # check diving into list from dict
                "not_secret_value",
                SECRET_PREFIX + "layer2_list_name_of_secret",
                {  # check diving into dict from list
                    "layer3_key1": "not_secret_value",
                    "layer3_key2": SECRET_PREFIX + "layer3_name_of_secret",
                },
                [  # check diving into list from list
                    "not_secret_value",
                    SECRET_PREFIX + "layer3_list_name_of_secret",
                ],
                123124,  # check handling of number values from list
            ],
            "layer1_key4": SECRET_PREFIX + "name_of_secret",
            "layer1_key5": 123,  # check handling of number values from dict
        })

        # the secret values that expected
        expected_secrets = [
            Secret(
                name_in_holder="layer2_name_of_secret",
                path_in_data=["layer1_key2", "layer2_key2"],
            ),
            Secret(
                name_in_holder="layer2_list_name_of_secret",
                path_in_data=["layer1_key3", 1],
            ),
            Secret(
                name_in_holder="layer3_list_name_of_secret",
                path_in_data=["layer1_key3", 3, 1],
            ),
            Secret(
                name_in_holder="name_of_secret",
                path_in_data=["layer1_key4"],
            ),
            Secret(
                name_in_holder="layer3_name_of_secret",
                path_in_data=["layer1_key3", 2, "layer3_key2"],
            ),
        ]
        # sort by path_in_data converted to string value
        self.sort_secrets(expected_secrets)

        # THE TEST
        # the method, that we testing
        secrets = config._search_for_secrets()

        self.sort_secrets(secrets)
        assert secrets == expected_secrets, 'check secrets with template'

    @pytest.mark.parametrize('name, secrets_to_resolve, expected_exception', [
        (
            'correct resolving',
            [
                Secret(
                    name_in_holder="name_1",
                    path_in_data=[],
                ),
                Secret(
                    name_in_holder="name_2",
                    path_in_data=[],
                ),
                Secret(
                    name_in_holder="name_3",
                    path_in_data=[],
                ),
            ],
            None,
        ),
        (
            'secrets with name dupls',
            [
                Secret(
                    name_in_holder="name_1",
                    path_in_data=[],
                ),
                Secret(
                    name_in_holder="name_2",
                    path_in_data=[],
                ),
                Secret(
                    name_in_holder="name_1",
                    path_in_data=[],
                ),
            ],
            SecretsReplaceException('duplications found'),
        ),
    ])
    def test_resolve_secrets(self, name, secrets_to_resolve, expected_exception):
        # set SecretsHolderStub as SecretsHolder that should be loaded from config info
        with patch.object(Config, '_load_secrets_holder_from_config', return_value=SecretsHolderStub()):
            try:
                resolved_secrets = config._resolve_secrets(secrets_to_resolve)
            except Exception as e:
                if expected_exception is not None:
                    assert isinstance(e, type(expected_exception)), \
                        f'invalid exception type catched {type(e)}; expected {type(expected_exception)}'
                    assert str(expected_exception) in str(e), \
                        f'invalid exception message: {e}; expected something that contains: {expected_exception}'
                    return
                else:
                    raise ConfigInternalsTestException(f'Unexpected exception caught: {e}')
            if expected_exception is not None:
                raise ConfigInternalsTestException('no exception has been caught, but expected {expected_exception}')

            # prepare template for successfull resolving cases
            # SecretsHolderStub just append suffix to secret name as a value of that secret
            expected_secrets = [Secret(
                name_in_holder = s.name_in_holder,
                path_in_data = s.path_in_data,
                value = s.name_in_holder + "_secret_value",
            ) for s in secrets_to_resolve]

            assert resolved_secrets == expected_secrets, 'check resolved_secrets with template'

    def test_resolve_secrets_check_secrets_holder_error(self):
        expected_exception_type = SecretsReplaceException
        expected_string_in_exception = 'secrets_holder'

        with patch.object(Config, '_load_secrets_holder_from_config', return_value=SecretsHolderStub(raise_error=True)):
            try:
                resolved_secrets = config._resolve_secrets([])
            except expected_exception_type as e:
                assert expected_string_in_exception in str(e), \
                    f'unexpected message of exception: "{e}"; substring "{expected_string_in_exception}" should present'
                return
            except Exception as e:
                raise ConfigInternalsTestException(f'unexpected exception caught: {type(e)}; should be one of type {expected_exception_type}')
            raise ConfigInternalsTestException(f"exception hasn't been caught; expected one of type {expected_exception_type}'")

    @pytest.mark.parametrize('starting_config_data, resolved_secrets, '+
                             'expected_data_after_replace, expected_exception', [
        pytest.param(
            {
                "layer1_key1": "not_secret_value",
                "layer1_key2": {  # check diving into dict from dict. First dict is the main node
                    "layer2_key1": "not_secret_value",
                    "layer2_key2": SECRET_PREFIX + "layer2_name_of_secret",
                },
                1: { # check diving next level from dict by number key
                    "layer2_key3": SECRET_PREFIX + "layer2_numdict_name_of_secret",
                    2: SECRET_PREFIX + "layer_2_allnumkeys_name_of_secret",
                },
                "layer1_key3": [  # check diving into list from dict
                    "not_secret_value",
                    SECRET_PREFIX + "layer2_list_name_of_secret",
                    {  # check diving into dict from list
                        "layer3_key1": "not_secret_value",
                        "layer3_key2": SECRET_PREFIX + "layer3_name_of_secret",
                    },
                    [  # check diving into list from list
                        "not_secret_value",
                        SECRET_PREFIX + "layer3_list_name_of_secret",
                    ],
                    123124,
                ],
                "layer1_key4": SECRET_PREFIX + "name_of_secret",
                "layer1_key5": 123,
            },
            [
               Secret(
                   name_in_holder="layer2_name_of_secret",
                   path_in_data=["layer1_key2", "layer2_key2"],
                   value="secret_real_value_1",
               ),
               Secret(
                   name_in_holder="layer2_list_name_of_secret",
                   path_in_data=["layer1_key3", 1],
                   value="secret_real_value_2",
               ),
               Secret(
                   name_in_holder="layer3_list_name_of_secret",
                   path_in_data=["layer1_key3", 3, 1],
                   value="secret_real_value_3",
               ),
               Secret(
                   name_in_holder="name_of_secret",
                   path_in_data=["layer1_key4"],
                   value="secret_real_value_4",
               ),
               Secret(
                   name_in_holder="layer3_name_of_secret",
                   path_in_data=["layer1_key3", 2, "layer3_key2"],
                   value="secret_real_value_5",
               ),
               Secret(
                   name_in_holder="layer2_numdict_name_of_secret",
                   path_in_data=[1, "layer2_key3"],
                   value="secret_real_value_6",
               ),
               Secret(
                   name_in_holder="layer_2_allnumkeys_name_of_secret",
                   path_in_data=[1, 2],
                   value="secret_real_value_7",
               )
            ],
            {
                "layer1_key1": "not_secret_value",
                "layer1_key2": {  # check diving into dict from dict. First dict is the main node
                    "layer2_key1": "not_secret_value",
                    "layer2_key2": "secret_real_value_1",
                },
                1: { # check diving next level from dict by number key
                    "layer2_key3": "secret_real_value_6",
                    2: "secret_real_value_7",
                },
                "layer1_key3": [  # check diving into list from dict
                    "not_secret_value",
                    "secret_real_value_2",
                    {  # check diving into dict from list
                        "layer3_key1": "not_secret_value",
                        "layer3_key2": "secret_real_value_5",
                    },
                    [  # check diving into list from list
                        "not_secret_value",
                        "secret_real_value_3",
                    ],
                    123124,  # check handling of number values from list
                ],
                "layer1_key4": "secret_real_value_4",
                "layer1_key5": 123,  # check handling of number values from dict
            },
            None,
            id = 'correct_replacing',
        ),
        pytest.param(
            {
                "layer1_key": [1,2,3,4],
            },
            [Secret(
                name_in_holder="name",
                path_in_data=["layer1_key", "some_key_instead_index"],
            )],
            None,
            SetValueByPathException("key and node has incompatible types"),
            id = 'try to set key value into array',
        ),
        pytest.param(
            {
                "layer1_key": [0,1,2],
            },
            [Secret(
                name_in_holder="name",
                path_in_data=["layer1_key", -10],
            )],
            None,
            SetValueByPathException("Negative index"),
            id = 'try to set negative array index',
        ),
        pytest.param(
            {
                "layer1_key": [0,1,2],
            },
            [Secret(
                name_in_holder="name",
                path_in_data=["layer1_key", 10],
            )],
            None,
            SetValueByPathException("index is larger or equal than length of list-node"),
            id = 'try to set to out of range index',
        ),
        pytest.param(
            {
                "key": "value"
            },
            [Secret(
                name_in_holder="Key_that_not_exist",
                path_in_data=["wrong_key"],
            )],
            None,
            SetValueByPathException("key doesn't exist in dict"),
            id = 'try to set into not existed key',
        ),
    ])
    def test_replace_secrets(
        self, starting_config_data, resolved_secrets,
        expected_data_after_replace, expected_exception,
    ):
        # TEST PREPARATION
        # set test data dict
        config._set_class_data(starting_config_data)

        # THE TEST
        try:
            config._replace_secrets(resolved_secrets)
        except Exception as e:
            if expected_exception is not None:
                assert isinstance(e, type(expected_exception)), \
                    f'invalid exception type catched {type(e)}; expected {type(expected_exception)}'
                assert str(expected_exception) in str(e), \
                    f'invalid exception message: {e}; expected something that contains {expected_exception}'
                return
            else:
                raise ConfigInternalsTestException(f'Unexpected exception caught: {e}')

        if expected_exception is not None:
            raise ConfigInternalsTestException('no exception has been caught, but expected {expected_exception}')

        assert config.data == expected_data_after_replace, \
            'check replaced config.data with template'
