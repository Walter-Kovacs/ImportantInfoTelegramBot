from components.config.config import config, SECRET_PREFIX, Secret

class TestConfigInternals:
    def test_secrets_searching_in_data(self):
        # set test data dict
        config._set_class_data({
            "layer1_key1": "not_secret_value",
            "layer1_key2": { # check diving into dict from dict. First dict is the main node
                "layer2_key1": "not_secret_value",
                "layer2_key2": SECRET_PREFIX + "layer2_name_of_secret",
            },
            "layer1_key3": [ # check diving into list from dict
                "not_secret_value",
                SECRET_PREFIX + "layer2_list_name_of_secret",
                { # check diving into dict from list
                    "layer3_key1": "not_secret_value",
                    "layer3_key2": SECRET_PREFIX + "layer3_name_of_secret",
                },
                [ # check diving into list from list
                   "not_secret_value",
                    SECRET_PREFIX + "layer3_list_name_of_secret",
                ],
                123124, # check handling of number values from list
            ],
            "layer1_key4": SECRET_PREFIX + "name_of_secret",
            "layer1_key5": 123, # check handling of number values from dict
        })

        # the secret values that expected
        expected_secrets = [
            Secret(
                name_in_holder = "layer2_name_of_secret",
                path_in_data = ["layer1_key2","layer2_key2"],
            ),
            Secret(
                name_in_holder = "layer2_list_name_of_secret",
                path_in_data = ["layer1_key3", 1],
            ),
            Secret(
                name_in_holder = "layer3_list_name_of_secret",
                path_in_data = ["layer1_key3", 3, 1],
            ),
            Secret(
                name_in_holder = "name_of_secret",
                path_in_data = ["layer1_key4"],
            ),
            Secret(
                name_in_holder = "layer3_name_of_secret",
                path_in_data = ["layer1_key3", 2, "layer3_key2"],
            ),
        ]
        # sort by path_in_data converted to string value
        expected_secrets.sort(key=lambda secret: '.'.join([str(item) for item in secret.path_in_data]))

        secrets = config._search_for_secrets()
        secrets.sort(key=lambda secret: '.'.join([str(item) for item in secret.path_in_data]))

        assert secrets == expected_secrets
