FreeKick Developer
==================


Configuring the Estimator or Forecast models
--------------------------------------------

We can now change the serialized model that each league uses for prediction
without the need for a code review. An environment variable of the format
"<LEAGUE-NAME>_ESTIMATOR_CLASS" can be defined in `production.env` or
`development.env` and the app will find and use the respective serial model
for this estimator class.
E.g.:

    .. code-block:: bash

        EPL_ESTIMATOR_CLASS=FreekickDecisionTreeClassifier

In the example above, this tells the app to use the `FreekickDecisionTreeClassifier`
model for English Primer League Predictions.
Once a change is made, only  restart of the app will be needed to pickup the
change.
