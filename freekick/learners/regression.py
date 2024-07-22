"""Model for various logistic models."""

from dask_ml.linear_model import LogisticRegression as dask_LR
from sklearn.linear_model import LogisticRegression as sklearn_LR

from freekick import _logger
from freekick.datastore.util import Backend, League

from .classification import BaseClassifier


class SoccerLogisticModel(BaseClassifier):
    def __init__(
        self, league: League, backend: Backend = Backend.PANDAS
    ) -> None:
        self.backend = backend
        super().__init__(league)

    def init_model(self):
        match self.backend:
            case Backend.PANDAS:
                learner = sklearn_LR
            case Backend.DASK:
                learner = dask_LR
            case _:
                raise ValueError(
                    f"{self.__class__} does not support backend {self.backend}"
                )

        _logger.info(f"Selected Backend: {self.backend}")
        return learner(penalty="l2", fit_intercept=False, C=1)
