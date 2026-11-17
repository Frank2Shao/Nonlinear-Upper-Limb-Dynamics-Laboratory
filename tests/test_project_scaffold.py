from importlib import import_module

from config.settings.base import PROJECT_APPS


def test_project_app_configs_are_importable_and_named_after_their_package() -> None:
    for dotted_path in PROJECT_APPS:
        module_path, class_name = dotted_path.rsplit(".", maxsplit=1)
        app_config = getattr(import_module(module_path), class_name)

        assert module_path == f"{app_config.name}.apps"
