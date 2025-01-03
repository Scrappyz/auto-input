## auto-input
A python program created to automate the mouse and keyboard.

## Table of Contents
- [auto-input](#auto-input)
- [Installation](#installation)
- [Usage](#usage)
- [Future Features](#future-features)

## Dependencies
- [Python 3](https://www.python.org/downloads/)
### Modules
- [bidict](https://pypi.org/project/bidict/)
- [pynput](https://pypi.org/project/pynput/)

## Installation
1. Clone the repository using `git clone`.
2. Navigate to the `auto-input` folder and run `pip install .`.
3. Run using `auto-input`.

## Usage
```
usage: autoinput.py [-h] [-v] [--set-record-dir SET_RECORD_DIR] {record,play} ...

positional arguments:
  {record,play}
    record              record input
    play                play a record

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --set-record-dir SET_RECORD_DIR
                        set the directory to store and look for records
```

### Recording
Record your input using the `record make <record-name> -mk` command:
```
autoinput record make "test" -mk
```
This command creates a record named test with both mouse and keyboard inputs enabled.

You will then encounter this prompt:
```
[READY] Press 'ctrl + shift' to start recording or press 'ctrl + z' to cancel
```
Press `ctrl + shift` to start recording. To pause, press `ctrl + alt`, and to stop, press `ctrl + z`.

Hotkeys are configurable with the `config set` command.

### Playing records
Play saved records using the play <record-name> command:
```
autoinput play "test"
```
This command plays the record named `test`.

To view saved records, use the command `record list` or `play -a`.

After entering the `play` command, you will see this prompt:
```
[READY] Press 'ctrl + shift' to start playback or press 'ctrl + z' to cancel
```
Press `ctrl + shift` to start playback. To pause, press `ctrl + alt`, and to stop, press `ctrl + z`.

Hotkeys are configurable with the `config set` command.

### Configuration
Edit config options in the `config.json` file generated where `autoinput.py` resides.

Alternatively, use the `config set <config-option> <value>` command:
```
autoinput config set "startHotkey" "ctrl + space"
``` 
This command sets the start hotkey to `ctrl + space`.