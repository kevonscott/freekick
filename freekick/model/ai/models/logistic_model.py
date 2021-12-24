"""Model for various logistic models."""

from sklearn.linear_model import LogisticRegression
import pandas as pd
import os
import pickle


class SoccerLogisticModel:
    def __init__(self, league, X, y) -> None:
        self.league = league
        self.model = None
        self.y = y
        self.X = X

    def fit(self):
        model = LogisticRegression(
            penalty="l2", fit_intercept=False, multi_class="ovr", C=1
        )
        # X_to_numpy = self.X.to_numpy().astype("float")
        # self.model = model.fit(X_to_numpy, self.y)
        self.model = model.fit(self.X, self.y)
        self.model.columns = None

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
        coeffs = coeffs.rename(columns={-1: "away_win", 0: "draw", 1: "home_win"})

        return coeffs

    def predict_winner(self, pred_data):
        """Predict the match winner"""
        self.check_fit()

        pred = self.model.predict(pred_data)

        df_pred = pd.DataFrame(pred, index=pred_data.index, columns=["Prediction"])
        return df_pred

    def predict_probability(self, X):
        """Predict the probabilities of draw or win for each team"""
        self.check_fit()

        df = pd.DataFrame(
            self.model.predict_proba(X), columns=self.model.classes_, index=X.index
        )
        df = df.rename(columns={-1: "away_win", 0: "draw", 1: "home_win"})

        return df

    def persist_model(self):
        """Persists a model as Pickle file on disk in models folder.
        Overrite if file already exists.

        Parameters
        ----------
        name : str, optional
            Name of the pickle file, by default 'soccer_model'
        """
        self.check_fit()
        serial_path = os.path.join(
            "freekick", "model", "ai", "serialized_models", self.league + ".pkl"
        )
        file_path = os.path.abspath(serial_path)
        with open(file_path, "wb") as mod_file:
            pickle.dump(self.model, mod_file)
        print(f"Model serialized to {file_path}")
