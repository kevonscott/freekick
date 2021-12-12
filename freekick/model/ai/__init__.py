"""Model for all Artificial Intelligence and Machine Learning Operations."""
import os
import pickle
import logging
import pkg_resources

logging.basicConfig()
_logger = logging.getLogger("AI")


def load_model(model_name: str):
    """Load serial models"""
    model_path = pkg_resources.resource_filename(
        __name__, os.path.join("serialized_models", model_name)
    )

    with open(model_path, "rb") as plk_file:
        model = pickle.load(plk_file)
        _logger.info(f"     Loaded: {model_name}")
    return model


# _logger.info(" Loading serial models...")
# serial_models = {
#     "epl": load_model(model_name="epl.pkl"),
#     "bundesliga": load_model(model_name="bundesliga.pkl"),
# }
