"""Classification Models for Freekick predictions."""

from abc import ABC, abstractmethod

import joblib
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.tree import DecisionTreeClassifier

from freekick import ESTIMATOR_LOCATION
from freekick.datastore.util import Backend, League
from freekick.utils import _logger
from freekick.utils.freekick_config import coerce_env_dir_name


class BaseClassifier(ABC):
    def __init__(self, league: League) -> None:
        self.league: League = league
        self.name = f"{self.league.value}_{self.__class__.__name__}"
        self.is_fit = False
        self.model = self.init_model()
        if not self.model:
            raise ValueError("self.init_model() must return an estimator!!")

    @abstractmethod
    def init_model(self) -> BaseEstimator:
        """Define, initialize and return your Classifier."""
        pass

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:  # type: ignore [type-arg]
        """Fit an estimator (self.model) to be used for prediction.

        :param X: Training data for the model.
        :param y: Target values or class labels for classification.
        """
        self.model = self.model.fit(X, y)
        self.features = X.columns
        self.is_fit = True

    def check_fit(self) -> None:
        """Check if self.model is fitted."""
        if not self.is_fit:
            raise NotImplementedError(
                "Model not trained: Please train/fit the model first using"
                "model.fit(X, y)."
            )

    def get_coeff(self) -> pd.DataFrame | None:
        """Get the coefficients of the classification labels."""
        self.check_fit()
        try:
            coeffs = pd.DataFrame(
                self.model.coef_,
                index=self.model.classes_,
                columns=self.features,
            ).T
        except AttributeError:
            # Not all estimator supports the concept of coefficients. In this
            # case, log and return None.
            _logger.info(f"Model {self.__class__} does not support '.coef_'")
            return None
        coeffs = coeffs.rename(
            columns={-1: "away_win", 0: "draw", 1: "home_win"}
        )
        return coeffs

    def predict(self, pred_data: pd.DataFrame) -> pd.DataFrame:
        """Predict the match winner."""
        self.check_fit()

        pred = self.model.predict(pred_data)

        df_pred = pd.DataFrame(
            pred, index=pred_data.index, columns=["Prediction"]
        )
        return df_pred

    def predict_probability(self, X: pd.DataFrame) -> pd.DataFrame:
        """Predict the probabilities each result."""
        self.check_fit()

        df = pd.DataFrame(
            self.model.predict_proba(X),
            columns=self.model.classes_,
            index=X.index,
        )
        df = df.rename(columns={-1: "away_win", 0: "draw", 1: "home_win"})

        return df

    def persist_model(self, env: str) -> None:
        """Serialize the model to disk. Overwrite if file already exists."""
        env_subdir = coerce_env_dir_name(env_name=env)
        self.check_fit()
        model_path = ESTIMATOR_LOCATION / env_subdir / f"{self.name}.pkl"
        joblib.dump(self.model, model_path)
        _logger.info(f"Model serialized to {model_path}")


class FreekickDecisionTreeClassifier(BaseClassifier):
    def __init__(
        self, league: League, backend: Backend = Backend.PANDAS
    ) -> None:
        self.backend = backend
        super().__init__(league)

    def init_model(self) -> DecisionTreeClassifier:
        match self.backend:
            case Backend.PANDAS:
                classifier = DecisionTreeClassifier
            case _:
                raise ValueError(
                    f"{self.__class__} does not support backend {self.backend}"
                )

        _logger.info(f"Selected Backend: {self.backend}")
        return classifier()


class FreekickSVMClassifier(BaseClassifier):
    def __init__(
        self, league: League, backend: Backend = Backend.PANDAS
    ) -> None:
        self.backend = backend
        super().__init__(league)

    def init_model(self) -> None:
        raise NotImplementedError


class FreekickKNNClassifier(BaseClassifier):
    def __init__(
        self, league: League, backend: Backend = Backend.PANDAS
    ) -> None:
        self.backend = backend
        super().__init__(league)

    def init_model(self) -> None:
        raise NotImplementedError
