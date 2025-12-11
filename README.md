# fairfield

Fairfield is a web application for viewing baseball metrics.
It is built on top of the [baseball_metrics](https://github.com/rockysnow7/baseball_metrics) library.

## Setup

1. Clone the repository and install the dependencies.
2. Download the retrosheet [CSV files](https://www.retrosheet.org/downloads/othercsvs.html) for each year to be made available. Place them in a directory called `retrosheet`.
3. Run the server with `fastapi run server.py`.
