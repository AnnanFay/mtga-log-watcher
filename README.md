# mtga-log-watcher
Auto-backup MTGA logs.

Backups are made when Arena is closed and a log file exists.

Backups are placed in `./named_logs` relative to default log file location (`%APPDATA%\..\LocalLow\Wizards Of The Coast\MTGA`)

## Usage

With directory set to the project:

`python cli.py --watch`

## Installation

Install python 3.8 or above.

Install requirements: `pip install -r requirements.txt`

## Known bugs

* There is no way of configuring program behaviour. (changing paths, etc.)
* Linux/Mac - 99% sure this is completely broken.
* The context menu is bad - slow and laggy. [TODO: Change to a different library]
* If the log file is locked at backup time it will successfully backup, but locked log will remain. This doesn't cause issues but is potentially confusing to users what is going on.


## Potential Issues

* Multiple watcher instances can be opened. Don't do this! [TODO: prevent this]
* Multiple MTGA instances can be open at the same time. Don't do this! [TODO: warn users]
