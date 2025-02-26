import sys
from pathlib import Path

from loguru import logger


def dump_to_file(agent, base, size, error, directory):
    """Reading bytes from session and saving it to a file"""
    try:
        filename = str(base) + "_dump.data"
        dump = agent.read_memory(base, size)
        file_path = Path(directory) / filename
        with file_path.open("wb") as f:
            f.write(dump)
        return error
    except PermissionError:
        logger.error(f"Permission denied to write to {directory}")
        sys.exit(1)
    except Exception as e:
        # Helps removing the current progress bar before printing the error message
        print(" " * 80 + "\r", end="", flush=True)
        logger.debug(str(e))
        logger.warning("Oops, memory access violation!")
        return error


def splitter(agent, base, size, max_size, error, directory):
    """Read bytes that are bigger than the max_size value, split them into chunks and save them to a file"""
    times = size // max_size
    diff = size % max_size
    if diff == 0:
        logger.debug("Number of chunks:" + str(times + 1))
    else:
        logger.debug("Number of chunks:" + str(times))
    global cur_base
    cur_base = int(base, 0)

    for time in range(times):
        logger.debug(f"Save bytes: {str(cur_base)} till {str(hex(cur_base+max_size))}")
        dump_to_file(agent, cur_base, max_size, error, directory)
        cur_base = cur_base + max_size

    if diff != 0:
        logger.debug(f"Save bytes: {str(cur_base)} till {str(hex(cur_base+diff))}")
        dump_to_file(agent, cur_base, diff, error, directory)
