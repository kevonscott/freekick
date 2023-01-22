from enum import Enum

# from .logistic_model import SoccerLogisticModel


class Backend(Enum):
    PANDAS = 1
    DASK = 2
