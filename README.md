# FreeKick (WORK-IN-PROGRESS)

FreeKick is a program designed to predict soccer games using statistical methods.
This project is in the EARLY PHASE OF DEVELOPMENT and will be iterated upon to create a
complete product. As a result of this project being in active development,
there will be frequent changes some of which might be breaking changes.

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
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
### Making predictions form the command line
Fom the root of the project, execute the command below specifying the codes for the league, home team and away team respectively.
```
./freekick/cli.py match --league epl --home ARS -away MCI
```
### Making predictions using the webapp
Fom the root of the project to launch the FreeKick app.
```bash
$ .venv/bin/python3 -m entrypoints.cli serve
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
```

### Query latest data and update database
```bash
NOTIMPLEMENTED
```



## License

Distributed under the MIT License. See `LICENSE.txt` for more information
