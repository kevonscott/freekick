=============
Release Notes
=============


Version 0.2
-----------

- Whats new in version 0.2.0

  - _LEAGUES has been renamed to League and is now an Enum.
  - Migrate handlers from Flask Blueprint to flask-restx.
  - DecisionTreeClassifier is now the default estimator instead of the previous LogisticRegression.
  - Predictions now support specifying match date, time and attendance from UI.
  - Added swagger endpoint at '/swagger'.
  - Stratify training dataset.
  - Day of week is now a feature in dataset.
  - Add win percentage and pythagorean expectation to dataset.
  - switch to joblib for sklearn model persistence
  - Set DataStore default to Database (SQLLite)
  - Ruff replaced black, flake8 and isort as default formatter and linter
  - Enable Mypy pre-commit project-wide
  - Ability to  update WPC and PYTH from admin_cli
  - The default estimator/model per league is now configurable via env variables
  - A default application data workspace is now added storing configurable app settings

Version 0.1
-----------

- Whats new in version 0.1.0

  - Added changelog.
  - data_maintainer data-type arg is now case sensitive.
  - Fix date parse pandas warning to parse date in more consistent format.
  - Code Refactor
  - Add support for dask backend


Version 0.0
-----------

- Whats new in version 0.0.3

  - Basic working prototype with only EPL and single match prediction.
