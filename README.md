# fridump3

Fridump is an open source memory dumping tool, primarily aimed to penetration testers and developers. Fridump is using the Frida framework to dump accessible memory addresses from any platform supported. It can be used from a Windows, Linux or Mac OS X system to dump the memory of an iOS, Android or Windows application.

## Fork information

This project is based on the following project: [https://github.com/Nightbringer21/fridump](https://github.com/Nightbringer21/fridump) and the pending PR concerning the python3 support (especially from [georgepetz](https://github.com/georgepetz) . Additionally I added the network support in addition to the USB support.

FYI: I will destroy this repo is the Fridump author will integrate the pending PR concerning Python3 support.

## Installation

Simply run one of the following commands:
> :warning: pipx is recommended for system or user wide installations
```
pipx install git+https://github.com/rootbsd/fridump3
pip install git+https://github.com/rootbsd/fridump3
```

## Usage
---

```
usage: fridump3 [-h] [-o dir] [-u] [-H HOST] [-r] [-s] [--max-size bytes]
                [--log-level {none,debug,info,warning,error,critical}]
                [--log-filename LOG_FILENAME]
                process

positional arguments:
  process               the process that you will be injecting to

options:
  -h, --help            show this help message and exit
  -o, --out dir         provide full output directory path. (def: "dump")
  -u, --usb             device connected over usb
  -H, --host HOST       device connected over IP
  -r, --read-only       dump read-only parts of memory. More data, more errors
  -s, --strings         run strings on all dump files. Saved in output dir.
  --max-size bytes      maximum size of dump file in bytes (def: 20971520)
  --log-level, -l {none,debug,info,warning,error,critical}
                        level of debug you wish to display.
  --log-filename LOG_FILENAME
                        output file used to store logs
```
