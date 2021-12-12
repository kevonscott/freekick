## About FreeKick (IN-PROGRESS)

FreeKick is a program designed to predict soccer games using statistical methods.
This project is in the EARLY PHASE OF DEVELOPMENT and will be iterated upon to create a
complete product.

### Built With
* [Flask](https://flask.palletsprojects.com/)
* [React.js](https://reactjs.org/)
* [HTML](https://en.wikipedia.org/wiki/HTML)
* [CSS](https://en.wikipedia.org/wiki/CSS)
* [JavaScript](https://www.javascript.com/)


## Getting Started

### Installation
1. Create and activate a virtual environment.
2. Run the command below in the projects main directory it install the required libraries.
    ```bash
    $ pip install -e .
    ```

## Usage
```bash
$ export FLASK_APP=freekick
$ export FLASK_ENV=development
$ flask run
```

## Retraining The Model
Retraining is done via the command line using the cli tool:
```bash
(soccer) USER@COMPUTER[~/src/freekick]:> python freekick/cli.py --help
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
(soccer) USER@COMPUTER[~/src/freekick]:>
```

### Re-fit and Persist the model to disk
```bash
python freekickp/cli.py -r epl --persist
```

### Query latest data and update database
```bash
NOTIMPLEMENTED
```



## License

Distributed under the MIT License. See `LICENSE.txt` for more information
