"""Model for all Machine Learning Operations."""

import pickle
from functools import lru_cache, partial
from typing import Any

from freekick import LEARNER_MODEL_LOCATION, _logger
from freekick.datastore.util import League


def _load_model(model_name: str):
    """Load and deserialize a model."""
    model_path = LEARNER_MODEL_LOCATION / model_name
    with open(model_path, "rb") as plk_file:
        model = pickle.load(plk_file)  # noqa B301
        _logger.debug(f"     - {model_name}")
    return model


@lru_cache()
def load_models() -> dict[str, Any]:
    _logger.debug(" Loading serialized models...")
    return {
        league.value: _load_model(model_name=f"{league.value}.pkl")
        for league in League
    }


serial_models = partial(load_models)
