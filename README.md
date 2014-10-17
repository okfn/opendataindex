# Open Data Index

This is the code that powers the [Open Data Index](http://index.okfn.org/).


## Setup

Some brief instructions, proper docs to come.

* Setup a virtual env
* Install dependencies: `pip install -r requirements.txt`
* `pelican content -o output -s pelicanconf.py`
* `./develop-server` to run a server that watches and builds

[Pelican documentation for more information](http://docs.getpelican.com)


## Deployment

Steps to create a snapshot for deployment::

    pelican content -o output -s publishconf.py
    ghp-import output
    git push origin gh-pages


## Data

Data is found in the `data` directory. This both powers the site build and is
usuable in its own right (as a Tabular Data Package).

### Preparation

Data is prepared by the python script `scripts/process.py`. This pulls data
from the Open Data Index Survey (Census), processes it in various ways and then
writes it to the `data` directory. If you want to

To run the script do:

    python scripts/process.py


## API

Open Data Index exposes a (simple) API for programmatic access to data. Currently, the API is available in both JSON and CSV formats.

### API endpoints

* {format} refers to either `json` or `csv`

#### /api/entries.{format}

Returns all entries in the database.


#### /api/entries/{year}.{format}

Returns entries sliced by year.

Available years:

* 2014
* 2013


#### /api/datasets.{format}

Returns all datasets in the database.


#### /api/datasets/{category}.{format}

Returns all datasets sliced by category, where `category` is a slugified string of the dataset category.

Available categories:

* civic-information
* environment
* finance
* geodata
* transport


#### /api/places.{format}

Returns all places in the database.


#### /api/questions.{format}

Returns all questions in the database.
