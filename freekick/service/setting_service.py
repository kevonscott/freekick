from .util import SettingDTO
from dataclasses import asdict

from freekick.utils.workspace import (
    load_runtime_settings, update_runtime_settings
)

def get_setting() -> SettingDTO:
    setting = {k.lower(): v for k,v in load_runtime_settings().items()}
    # TODO:Include real models
    setting['models'] = ["Model A", "Model B", "Model C", "Model D"]
    return SettingDTO(**setting)


def update_setting(setting: SettingDTO) -> None:
    update_runtime_settings(asdict(setting))