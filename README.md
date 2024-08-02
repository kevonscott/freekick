# FreeKick - Open Football Prediction

FreeKick is a program designed to predict soccer games using statistical methods.
This project is in the EARLY PHASE OF DEVELOPMENT and will be iterated upon to create a
complete product. As a result of this project being in active development,
there will be frequent changes some of which might be breaking changes.

# Demo

https://github.com/user-attachments/assets/4e796f93-59f1-470f-83a3-e9c12ab7e175



### Built With
* [Python](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/)
* [HTML](https://en.wikipedia.org/wiki/HTML)
* [CSS](https://en.wikipedia.org/wiki/CSS)
* [JavaScript](https://www.javascript.com/)

# Disclaimer
This software is for educational and entertainment purposes ONLY. Do not use this
software to risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR
OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR ANY
FINANCIAL LOSS RESULTING FROM THE USAGE OF THIS SOFTWARE.

# Getting Started
Create virtual env and install requirements
```
git clone https://github.com/kevonscott/freekick.git
cd freekick
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pre-commit install
```

## Usage
### Making predictions form the command line
Fom the root of the project, execute the command below specifying the codes for the league, home team and away team respectively.
```
.venv/bin/python3 -m entrypoints.cli match -l epl -r LIV -a ARS

INFO:FREEKICK:Request Type: Single Match Prediction
 League         HomeTeam        AwayTeam        Time    Date
 League.EPL     LIV             ARS             None    None

INFO:FREEKICK:MatchDTO(home_team='LIV', away_team='ARS', predicted_winner='Draw')
```
### Making predictions using the webapp
Fom the root of the project to launch the FreeKick app.
```bash
$ ./entrypoints/launch-dev.sh
```

## Retraining The Model
Retraining is done via the command line using the cli tool:
```bash
.venv/bin/python3 -m freekick.admin_cli --help
Usage: cli.py [OPTIONS]

Options:
  -r, --retrain [epl|bundesliga]  Retrain model
  -l, --list                      List current models
  -p, --persist                   Serialize model to disk if provided.
  -s, --size FLOAT                Training Size.  [default: 0.2]
  -s, --source [CSV|DATABASE]     Source of the training data. Default is CSV.
                                  If CSV, place the csv data file with the
                                  same name as the model in the data directory
                                  [default: CSV]
  --help                          Show this message and exit.

```

### Re-fit and Persist the model to disk
```bash
.venv/bin/python3 -m freekick.admin_cli -r epl --persist

INFO:FREEKICK:Retraining League.EPL...
INFO:FREEKICK:Selected Backend: Backend.PANDAS
INFO:FREEKICK:==================Model Statistics=========================
INFO:FREEKICK:Model Type: DecisionTreeClassifier()
INFO:FREEKICK:Model Name: epl
INFO:FREEKICK:Accuracy: 0.42109669317706155
INFO:FREEKICK:Model serialized to freekick/data/learner_model/epl.pkl
```

### Query latest data and update database
```bash
.venv/bin/python3 -m entrypoints.data_maintainer update -d current_season -l EPL -p

INFO:FREEKICK:Updating data for season 'S_2023_2024' and datastore 'DataStore.CSV'
INFO:FREEKICK:Fetching S_2023_2024 data from https://www.football-data.co.uk/mmz4281/2324/E0.csv...
INFO:FREEKICK:Loaded data successfully.
INFO:FREEKICK:Saving/Updating raw season file: freekick/data/raw/epl/season_2023-2024.csv
INFO:FREEKICK:Regenerating league data...
INFO:FREEKICK:freekick/data/raw/epl/season*.csv
INFO:FREEKICK:Persisting data: freekick/data/processed/epl.csv
INFO:FREEKICK:df.shape: (11944, 9)
INFO:FREEKICK:Updating data for season 'S_2023_2024' and datastore 'DataStore.DATABASE'
INFO:FREEKICK:Fetching S_2023_2024 data from https://www.football-data.co.uk/mmz4281/2324/E0.csv...
INFO:FREEKICK:Loaded data successfully.
INFO:FREEKICK:Updating Database...
```



## License

Distributed under the MIT License. See [LICENSE.txt](/LICENSE.txt) for more information
