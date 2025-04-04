"""Model for various logistic models."""

from sklearn.linear_model import LogisticRegression as sklearn_LR
from sklearn.base import BaseEstimator

from freekick.datastore.util import Backend, League
from freekick.utils import _logger

from .classification import BaseClassifier


class SoccerLogisticModel(BaseClassifier):
    def __init__(
        self, league: League, backend: Backend = Backend.PANDAS
    ) -> None:
        self.backend = backend
        super().__init__(league)

    def init_model(self) -> BaseEstimator:
        match self.backend:
            case Backend.PANDAS:
                learner = sklearn_LR
            case Backend.DASK:
                raise ValueError(
                    "Dask backend not yet fully supported!"
                )
            case _:
                raise ValueError(
                    f"{self.__class__} does not support backend {self.backend}"
                )

        _logger.info(f"Selected Backend: {self.backend}")
        return learner(penalty="l2", fit_intercept=False, C=1)
