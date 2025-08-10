"""
This functions are used for logging details while running scripts manually.
"""

import sys


def console_log(message):
    sys.stdout.write(" " * 50 + "\r")
    sys.stdout.flush()
    print(message)


def console_log_candidate_filtering(fileset_count):
    sys.stdout.write(f"Filtering Candidates - Fileset {fileset_count}\r")
    sys.stdout.flush()


def console_log_file_update(fileset_count):
    sys.stdout.write(f"Updating files - Fileset {fileset_count}\r")
    sys.stdout.flush()


def console_log_matching(fileset_count):
    sys.stdout.write(f"Performing Match - Fileset {fileset_count}\r")
    sys.stdout.flush()


def console_log_detection(fileset_count):
    sys.stdout.write(f"Processing - Fileset {fileset_count}\r")
    sys.stdout.flush()


def console_log_total_filesets(file_path):
    count = 0
    with open(file_path, "r") as f:
        for line in f:
            if line.strip().startswith("game ("):
                count += 1
    print(f"Total filesets present - {count}.")
