import argparse
import sys
import textwrap
from pathlib import Path

import frida
import frida.core
from loguru import logger

from fridump3.src import dumper, utils

logo = r"""
        ______    _     _
        |  ___|  (_)   | |
        | |_ _ __ _  __| |_   _ _ __ ___  _ __
        |  _| '__| |/ _` | | | | '_ ` _ \| '_ \\
        | | | |  | | (_| | |_| | | | | | | |_) |
        \_| |_|  |_|\__,_|\__,_|_| |_| |_| .__/
                                         | |
                                         |_|
        """


def set_log_level(level, output_file):
    """Sets the log level and log file.

    Args:
        level -- the log level to display (default "info")
        output_file -- the file used to output logs, including commands
    """
    logger.remove()  # Remove any default handlers
    if level.upper() != "NONE":
        LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>"
        logger.add(sys.stderr, format=LOG_FORMAT, level=level.upper())
        if output_file:
            logger.debug(f"Initializing logfile")
            try:
                logger.add(
                    output_file,
                    rotation="10 MB",
                    retention="30 days",
                    level=level.upper(),
                    format=LOG_FORMAT,
                )
            except PermissionError:
                logger.critical(
                    f"Permission denied to write to {output_file}, continuing without logs"
                )
        logger.debug(f"Logger initialized to {level.upper()}")


def MENU():
    parser = argparse.ArgumentParser(
        prog="fridump3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(""),
    )

    parser.add_argument("process", help="name of the process to dump memory from")
    parser.add_argument(
        "-o",
        "--out",
        type=str,
        help='provide full output directory path. (def: "dump").',
        metavar="DUMP_DIRECTORY",
    )
    parser.add_argument(
        "-u", "--usb", action="store_true", help="device connected over usb."
    )
    parser.add_argument("-H", "--host", type=str, help="device connected over IP.")
    parser.add_argument(
        "-r",
        "--read-only",
        action="store_true",
        help="dump read-only parts of memory. More data, more errors.",
    )
    parser.add_argument(
        "-s",
        "--strings",
        action="store_true",
        help="run strings on all dump files. Saved in output dir.",
    )
    parser.add_argument(
        "--max-size",
        type=int,
        help="maximum size of dump file in bytes (def: 20971520)",
        metavar="bytes",
    )
    parser.add_argument(
        "--log-level",
        "-l",
        choices=["none", "debug", "info", "warning", "error", "critical"],
        default="info",
        help="level of debug you wish to display.",
    )
    parser.add_argument(
        "--log-filename",
        default=None,
        help="output file used to store logs.",
    )
    args = parser.parse_args()
    return args

@logger.catch
def run() -> None:
    print(logo)

    arguments = MENU()

    # Define configurations
    APP_NAME = utils.normalize_app_name(appName=arguments.process)
    DIRECTORY = ""
    USB = arguments.usb
    IP = None
    STRINGS = arguments.strings
    MAX_SIZE = 20971520
    PERMS = "rw-"

    if arguments.host is not None:
        IP = arguments.host

    if arguments.read_only:
        PERMS = "r--"

    set_log_level(arguments.log_level, arguments.log_filename)

    # Start a new session
    session = None
    try:
        if USB:
            session = frida.get_usb_device().attach(APP_NAME)
        elif IP:
            session = frida.get_device_manager().add_remote_device(IP).attach(APP_NAME)
        else:
            session = frida.attach(APP_NAME)
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)

    # Selecting output directory
    if arguments.out is not None:
        DIRECTORY = Path(arguments.out)
        if DIRECTORY.is_dir():
            logger.info(f"Output directory is set to: {DIRECTORY}")
    else:
        current_dir = Path.cwd()
        logger.info(f"Current directory: {current_dir}")
        DIRECTORY = current_dir / "dump"
        logger.info(f"Output directory is set to: {DIRECTORY}")

    if not DIRECTORY.exists():
        logger.info(f"Creating directory {DIRECTORY}")
        try:
            DIRECTORY.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            logger.error(f"Permission denied to create {DIRECTORY}")
            sys.exit(1)

    mem_access_viol = ""

    logger.info("Starting memory dump")

    def on_message(message, data):
        print("[on_message] message:", message, "data:", data)

    script = session.create_script(
        """'use strict';

    rpc.exports = {
        enumerateRanges: async function (prot) {
            const ranges = await Process.enumerateRanges(prot);
            return ranges;
        },
        readMemory: function (address, size) {
            return ptr(address).readByteArray(size);
        }
    };
    """
    )
    script.on("message", on_message)
    script.load()

    agent = script.exports_sync
    ranges = agent.enumerate_ranges(PERMS)

    if arguments.max_size is not None:
        MAX_SIZE = arguments.max_size

    i = 0
    l = len(ranges)

    try:
        # Performing the memory dump
        for range in ranges:
            logger.debug(f"Base address: {str(range["base"])}")
            logger.debug(f"Size: {str(range["size"])}")
            if range["size"] > MAX_SIZE:
                logger.debug("Size is too big, splitting the dump into chunks")
                mem_access_viol = dumper.splitter(
                    agent,
                    range["base"],
                    range["size"],
                    MAX_SIZE,
                    mem_access_viol,
                    DIRECTORY,
                )
                continue
            mem_access_viol = dumper.dump_to_file(
                agent, range["base"], range["size"], mem_access_viol, DIRECTORY
            )
            i += 1
            utils.printProgress(i, l, prefix="Progress:", suffix="Complete", bar=50)
        print("")

        # Run Strings if selected
        if STRINGS:
            files = list(
                DIRECTORY.iterdir()
            )  # Get all items in the directory as Path objects
            total_files = len(files)

            logger.info("Running strings on all files")

            for i, file in enumerate(files, start=1):
                utils.strings(file.name, DIRECTORY)  # Pass only the filename if needed
                utils.printProgress(
                    i, total_files, prefix="Progress:", suffix="Complete", bar=50
                )
            print("")
    except KeyboardInterrupt:
        # Helps removing the current progress bar before printing the error message
        print(" " * 80 + "\r", end="\n", flush=True)
        logger.success(f"Exiting gracefully.")
        sys.exit(0)
    logger.success("Finished!")
