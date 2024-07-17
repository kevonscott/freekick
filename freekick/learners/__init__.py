from freekick.learners.learner_utils import serial_models

from .classification import FreekickDecisionTreeClassifier
from .regression import SoccerLogisticModel

DEFAULT_ESTIMATOR = FreekickDecisionTreeClassifier

__all__ = [
    "serial_models",
    "SoccerLogisticModel",
    "FreekickDecisionTreeClassifier",
    "DEFAULT_ESTIMATOR",
]
