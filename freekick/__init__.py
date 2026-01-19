import platform
from pathlib import Path

from packaging.version import Version

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data" # TODO: move to workspace dir
ESTIMATOR_LOCATION = DATA_DIR / "learner_model"  # TODO: move to workspace dir
# Ensure we are using the min_supported_platform
# We also need to ensure this only executes once and not all imports.
_PLATFORM_CHECK = False
if not _PLATFORM_CHECK:
    min_supported_platform = Version("3.11.0")
    current_platform = Version(platform.python_version())
    if current_platform < min_supported_platform:
        raise RuntimeError(
            f"Unsupported platform {current_platform}! The minimum supported"
            f" Python version is {min_supported_platform}"
        )
    _PLATFORM_CHECK = True
