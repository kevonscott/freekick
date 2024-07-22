"""Classification Models for Freekick predictions."""

import pickle
from abc import ABC, abstractmethod

import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.tree import DecisionTreeClassifier

from freekick import ESTIMATOR_LOCATION, _logger
from freekick.datastore.util import Backend, League


class BaseClassifier(ABC):
    def __init__(self, league: League) -> None:
        self.league: League = league
        # TODO: Use league and classname combo for model name
        # self.name = f"{self.league.value}_{self.__class__.__name__}"
        self.name = self.league.value
        self.is_fit = False
        self.model = self.init_model()
        if not self.model:
            raise ValueError("self.init_model() must return an estimator!!")

    @abstractmethod
    def init_model(self) -> BaseEstimator:
        """Define, initialize and return your Classifier."""
        pass

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
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

    def predict(self, pred_data) -> pd.DataFrame:
        """Predict the match winner."""
        self.check_fit()

        pred = self.model.predict(pred_data)

        df_pred = pd.DataFrame(
            pred, index=pred_data.index, columns=["Prediction"]
        )
        return df_pred

    def predict_probability(self, X) -> pd.DataFrame:
        """Predict the probabilities each result."""
        self.check_fit()

        df = pd.DataFrame(
            self.model.predict_proba(X),
            columns=self.model.classes_,
            index=X.index,
        )
        df = df.rename(columns={-1: "away_win", 0: "draw", 1: "home_win"})

        return df

    def persist_model(self) -> None:
        """Persists a model as Pickle file on disk in models folder.
        Overwrite if file already exists.

        Parameters
        ----------
        name : str, optional
            Name of the pickle file, by default 'soccer_model'
        """
        self.check_fit()
        model_path = ESTIMATOR_LOCATION / f"{self.name}.pkl"
        with open(model_path, "wb") as mod_file:
            pickle.dump(self.model, mod_file)
        _logger.info(f"Model serialized to {model_path}")


class FreekickDecisionTreeClassifier(BaseClassifier):
    def __init__(
        self, league: League, backend: Backend = Backend.PANDAS
    ) -> None:
        self.backend = backend
        super().__init__(league)

    def init_model(self):
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
    def __init__(self, league, backend: Backend = Backend.PANDAS) -> None:
        self.backend = backend
        super().__init__(league)

    def init_model(self):
        raise NotImplementedError


class FreekickKNNClassifier(BaseClassifier):
    def __init__(self, league, backend: Backend = Backend.PANDAS) -> None:
        self.backend = backend
        super().__init__(league)

    def init_model(self):
        raise NotImplementedError
