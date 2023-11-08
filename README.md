## auto-input
A python program created to automate the mouse and keyboard.

## Table of Contents
- [auto-input](#auto-input)
- [Installation](#installation)
- [Usage](#usage)

## Installation
1. Go to [releases]()
2. Download the executable.
3. Place the executable in an empty directory.
4. Run the executable in the command-line.

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
You can record your input by using `record add <record-name> -mk` subcommand like so:
```
autoinput record add "test" -mk
```
In this command, we are making a record named `test` with the mouse and keyboard enabled by the `-m` and `-k` flag.

You will then encounter this prompt:
```
[READY] Press 'ctrl + shift' to start recording or press 'ctrl + z' to cancel
```
To start the recording, press the `left-ctrl` and `left-shift` button then press them again to end the recording.

### Playing records
You can play your saved records by using the `play <record-name>` subcommand like so:
```
autoinput play "test"
```
In this command, we are going to play the record called `test`.

To view your saved records use the command `record list` or `play -a`.

After entering the `play` command, you will see this prompt:
```
[READY] Press 'ctrl + shift' to start playback or press 'ctrl + z' to cancel
```
To start the playback, press the `left-ctrl` and `left-shift` button then press them again to end the playback.

## Future Features
- Auto-presser
- Customizable hotkeys
- Better input tracking