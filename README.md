# Open Data Index

This is the code that powers the [Open Data Index](http://index.okfn.org/).

Just ported from Jekyll to Pelican. No docs yet. See [Pelican docs](http://docs.getpelican.com)

### but briefly

* setup a virtual env
* pip install -r requirements.txt
* pelican content to build, or ./develop-server to run a server that watches and builds


## Data

Data is found in the `data` directory. This both powers the site build and is
usuable in its own right (as a Tabular Data Package).

### Preparation

Data is prepared by the python script `scripts/process.py`. This pulls data
from the Open Data Index Survey (Census), processes it in various ways and then
writes it to the `data` directory. If you want to 

To run the script do:

    python scripts/process.py

