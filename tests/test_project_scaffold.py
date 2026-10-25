from importlib import import_module

from config.settings.base import PROJECT_APPS

EXPECTED_APP_CONFIGS = {
    "apps.core.apps.CoreConfig": "apps.core",
    "apps.accounts.apps.AccountsConfig": "apps.accounts",
    "apps.members.apps.MembersConfig": "apps.members",
    "apps.events.apps.EventsConfig": "apps.events",
    "apps.locations.apps.LocationsConfig": "apps.locations",
    "apps.safety.apps.SafetyConfig": "apps.safety",
}


def load_app_config(dotted_path: str):
    module_path, class_name = dotted_path.rsplit(".", maxsplit=1)
    module = import_module(module_path)
    return getattr(module, class_name)


def test_expected_app_configs_are_importable_and_named_correctly() -> None:
    actual_names = {
        dotted_path: load_app_config(dotted_path).name for dotted_path in PROJECT_APPS
    }

    assert actual_names == EXPECTED_APP_CONFIGS


def test_no_extra_project_apps_are_registered() -> None:
    assert set(PROJECT_APPS) == set(EXPECTED_APP_CONFIGS)
