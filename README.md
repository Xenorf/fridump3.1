# fridump3.1

Fridump is an open source memory dumping tool, primarily aimed to penetration testers and developers. Fridump is using the Frida framework to dump accessible memory addresses from any platform supported. It can be used from a Windows, Linux or Mac OS X system to dump the memory of an iOS, Android or Windows application.

## Requirements

- **Python** 3.7+
- **Frida** 17+

## Installation

Simply run one of the following commands:
> :warning: pipx is recommended for system or user wide installations
```
pipx install git+https://github.com/Xenorf/fridump3
pip install git+https://github.com/Xenorf/fridump3
```

## Usage

---

```
usage: fridump3 [-h] [-o dir] [-u] [-H HOST] [-r] [-s] [--max-size bytes]
                [--log-level {none,debug,info,warning,error,critical}]
                [--log-filename LOG_FILENAME]
                process

positional arguments:
  process               the process name, not package name that you will be injecting to

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
