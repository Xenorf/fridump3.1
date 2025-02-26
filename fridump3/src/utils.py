import re
from pathlib import Path

from loguru import logger


def printProgress(times, total, prefix="", suffix="", decimals=2, bar=100):
    """Print a progress bar"""
    filled = int(round(bar * times / float(total)))
    percents = round(100.00 * (times / float(total)), decimals)
    bar = "#" * filled + "-" * (bar - filled)
    print(f"{prefix} [{bar}] {percents}% {suffix} ", end="\r", flush=True)


def strings(filename, directory, min=4):
    """A very basic implementations of Strings"""
    strings_file = Path(directory) / "strings.txt"
    path = Path(directory) / filename
    with open(path, encoding="Latin-1") as infile:
        str_list = re.findall(r"[A-Za-z0-9/\-:;.,_$%'!()[\]<> \#]+", infile.read())
        with open(strings_file, "a") as st:
            for string in str_list:
                if len(string) > min:
                    logger.debug(string)
                    st.write(f"{string}\n")


def normalize_app_name(appName=str):
    """Normalize the name of application works better on frida"""
    try:
        appName = int(appName)
    except ValueError:
        pass
    return appName
