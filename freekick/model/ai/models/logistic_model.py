"""Model for various logistic models."""

import os
import pickle

import pandas as pd
from dask_ml.linear_model import LogisticRegression as dask_LR
from sklearn.linear_model import LogisticRegression as sklearn_LR

from freekick import _logger

from . import Backend


class SoccerLogisticModel:
    def __init__(
        self, league, X, y, backend: Backend = Backend.PANDAS
    ) -> None:
        self.league = league
        self.model = None
        self.y = y
        self.X = X
        self.backend = backend

        self.initialize_backend()

    def initialize_backend(self):
        self.logistic_regression = (
            dask_LR if self.backend == Backend.DASK else sklearn_LR
        )
        _logger.info(f"Selected Backend: {self.logistic_regression}")

    def fit(self):
        model = self.logistic_regression(
            penalty="l2", fit_intercept=False, multi_class="ovr", C=1
        )
        self.model = model.fit(self.X, self.y)

    def check_fit(self):
        if not self.model:
            raise NotImplementedError(
                "Model not trained: Please train/fit the model first using"
                "SoccerLogisticModel.fit()."
            )

    def get_coeff(self):
        # get the coefficients of three logistic models for each team.
        self.check_fit()

        coeffs = pd.DataFrame(
            self.model.coef_, index=self.model.classes_, columns=self.X.columns
        ).T
        coeffs = coeffs.rename(
            columns={-1: "away_win", 0: "draw", 1: "home_win"}
        )

        return coeffs

    def predict_winner(self, pred_data):
        """Predict the match winner"""
        self.check_fit()

        pred = self.model.predict(pred_data)

        df_pred = pd.DataFrame(
            pred, index=pred_data.index, columns=["Prediction"]
        )
        return df_pred

    def predict_probability(self, X):
        """Predict the probabilities of draw or win for each team"""
        self.check_fit()

        df = pd.DataFrame(
            self.model.predict_proba(X),
            columns=self.model.classes_,
            index=X.index,
        )
        df = df.rename(columns={-1: "away_win", 0: "draw", 1: "home_win"})

        return df

    def persist_model(self):
        """Persists a model as Pickle file on disk in models folder.
        Overwrite if file already exists.

        Parameters
        ----------
        name : str, optional
            Name of the pickle file, by default 'soccer_model'
        """
        self.check_fit()
        serial_path = os.path.join(
            "freekick",
            "model",
            "ai",
            "serialized_models",
            self.league + ".pkl",
        )
        file_path = os.path.abspath(serial_path)
        with open(file_path, "wb") as mod_file:
            pickle.dump(self.model, mod_file)
        print(f"Model serialized to {file_path}")
