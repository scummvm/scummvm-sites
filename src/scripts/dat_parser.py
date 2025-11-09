import argparse
import logging
import os
import re
import sys
import traceback
from src.scripts.db_functions import db_insert, match_fileset

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s'
)

def remove_quotes(string):
    # Remove quotes from value if they are present
    if string and string[0] == '"':
        string = string[1:-1]

    return string


def map_checksum_data(content_string):
    arr = []
    content_string = content_string.strip().strip("()").strip()

    tokens = re.split(r'\s+(?=(?:[^"]*"[^"]*")*[^"]*$)', content_string)

    current_rom = {}
    i = 0
    while i < len(tokens):
        if tokens[i] == "name":
            current_rom["name"] = tokens[i + 1].strip('"')
            i += 2
        elif tokens[i] == "size":
            current_rom["size"] = int(tokens[i + 1])
            i += 2
        elif tokens[i] == "size-r":
            current_rom["size-r"] = int(tokens[i + 1])
            i += 2
        elif tokens[i] == "size-rd":
            current_rom["size-rd"] = int(tokens[i + 1])
            i += 2
        elif tokens[i] == "modification-time":
            current_rom["modification-time"] = tokens[i + 1]
            i += 2
        else:
            checksum_key = tokens[i]
            checksum_value = tokens[i + 1] if len(tokens) >= 6 else "0"
            current_rom[checksum_key] = checksum_value
            i += 2

    arr.append(current_rom)

    return arr


def map_key_values(content_string, arr):
    # Split by newline into different pairs
    temp = content_string.splitlines()

    # Add pairs to the dictionary if they are not parentheses
    for pair in temp:
        pair = pair.strip()
        if pair == "(" or pair == ")":
            continue
        pair = list(map(str.strip, pair.split(None, 1)))
        pair[1] = remove_quotes(pair[1])

        # Handle duplicate keys (if the key is rom) and add values to a array instead
        if pair[0] == "rom":
            if "rom" not in arr:
                arr["rom"] = []
            arr["rom"].extend(map_checksum_data(pair[1]))
        else:
            arr[pair[0]] = pair[1].replace("\\", "")

    return arr


def match_outermost_brackets(input):
    """
    Parse DAT file and separate the contents each segment into an array.
    Segments are of the form `scummvm ( )`, `game ( )` etc.
    """
    matches = []
    depth = 0
    inside_quotes = False
    cur_index = 0
    line_number = 1
    index_line = 1

    for i, char in enumerate(input):
        if char == "\n":
            line_number += 1
            inside_quotes = False

        if char == '"' and input[i - 1] != "\\":
            inside_quotes = not inside_quotes

        elif char == "(" and not inside_quotes:
            if depth == 0:
                if "rom" in input[i - 4 : i]:
                    raise ValueError(
                        f"Missing an opening '(' for the game. Look near line {line_number}."
                    )
                index_line = line_number
                cur_index = i
            depth += 1

        elif char == ")" and not inside_quotes:
            if depth == 0:
                logging.warning(f"Unmatched ')' at line {line_number}")
                continue
            depth -= 1
            if depth == 0:
                match = input[cur_index : i + 1]
                matches.append((match, cur_index))

    if depth != 0:
        raise ValueError(
            f"Unmatched '(' starting at line {index_line}: possibly an unclosed block."
        )

    return matches


def parse_dat(dat_filepath):
    """
    Take DAT filepath as input and return parsed data in the form of
    associated arrays
    """
    if not os.path.isfile(dat_filepath):
        logger.error(f"File does not exist or is unreadable: {dat_filepath}.")
        return None

    try:
        with open(dat_filepath, "r", encoding="utf-8") as dat_file:
            content = dat_file.read()
    except (IOError, UnicodeDecodeError) as e:
        logger.error(f"Failed to read file {dat_filepath}: {e}")
        return None

    header = {}
    game_data = []
    resources = {}

    try:
        matches = match_outermost_brackets(content)
    except Exception as e:
        logger.error(f"Failed to parse outer brackets in {dat_filepath}: {e}")
        return None
    if matches:
        for data_segment in matches:
            try:
                if (
                    "clrmamepro" in content[data_segment[1] - 11 : data_segment[1]]
                    or "scummvm" in content[data_segment[1] - 8 : data_segment[1]]
                ):
                    header = map_key_values(data_segment[0], header)
                elif "game" in content[data_segment[1] - 5 : data_segment[1]]:
                    temp = {}
                    temp = map_key_values(data_segment[0], temp)
                    game_data.append(temp)
                elif "resource" in content[data_segment[1] - 9 : data_segment[1]]:
                    temp = {}
                    temp = map_key_values(data_segment[0], temp)
                    resources[temp["name"]] = temp
            except Exception as e:
                logger.error(f"Failed to parse a data_segment: {e}")
                return None

    return header, game_data, resources, dat_filepath


def main():
    try:
        parser = argparse.ArgumentParser(
            description="Process DAT files and interact with the database."
        )
        parser.add_argument(
            "--upload", nargs="+", help="Upload DAT file(s) to the database"
        )
        parser.add_argument(
            "--match", nargs="+", help="Populate matching games in the database"
        )
        parser.add_argument("--user", help="Username for database")
        parser.add_argument(
            "-r", help="Recurse through directories", action="store_true"
        )
        parser.add_argument("--skiplog", help="Skip logging dups", action="store_true")

        args = parser.parse_args()

        if not args.upload and not args.match:
            logger.error("No action specified. Use --upload or --match")
            parser.print_help()
            sys.exit(1)

        if args.upload:
            for filepath in args.upload:
                try:
                    parsed_data = parse_dat(filepath)
                    if parsed_data is not None:
                        db_insert(parsed_data, args.user, args.skiplog)
                    else:
                        logger.error(f"Failed to parse file for upload: {filepath}")
                except Exception as e:
                    logger.error(f"Error uploading {filepath}.")
                    raise e

        if args.match:
            for filepath in args.match:
                try:
                    parsed_data = parse_dat(filepath)
                    if parsed_data is not None:
                        match_fileset(parsed_data, args.user, args.skiplog)
                    else:
                        logger.error(f"Failed to parse file for matching: {filepath}")
                except Exception as e:
                    logger.error(f"Unable to match {filepath}:")
                    raise e

    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        sys.exit(0)
    except Exception:
        traceback.print_exc()
        logger.error(
            "Could not handle the exception. Look through the traceback and open an issue at: https://github.com/scummvm/scummvm-sites/issues"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
