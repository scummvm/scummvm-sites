import re
import os
import sys
from db_functions import db_insert, populate_matching_games, match_fileset
import argparse

def remove_quotes(string):
    # Remove quotes from value if they are present
    if string and string[0] == "\"":
        string = string[1:-1]

    return string

def map_checksum_data(content_string):
    arr = []
    
    content_string = content_string.strip().strip('()').strip()
    
    tokens = re.split(r'\s+(?=(?:[^"]*"[^"]*")*[^"]*$)', content_string)
    
    current_rom = {}
    i = 0
    while i < len(tokens):
        if tokens[i] == 'name':
            current_rom['name'] = tokens[i + 1].strip('"')
            i += 2
        elif tokens[i] == 'size':
            current_rom['size'] = int(tokens[i + 1])
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
            if 'rom' not in arr:
                arr['rom'] = []
            arr['rom'].extend(map_checksum_data(pair[1]))
        else:
            arr[pair[0]] = pair[1].replace("\\", "")
            
    return arr
            
def match_outermost_brackets(input):
    """
    Parse DAT file and separate the contents each segment into an array
    Segments are of the form `scummvm ( )`, `game ( )` etc.
    """
    matches = []
    depth = 0
    inside_quotes = False
    cur_index = 0

    for i in range(len(input)):
        char = input[i]

        if char == '(' and not inside_quotes:
            if depth == 0:
                cur_index = i
            depth += 1
        elif char == ')' and not inside_quotes:
            depth -= 1
            if depth == 0:
                match = input[cur_index:i+1]
                matches.append((match, cur_index))
        elif char == '"' and input[i - 1] != '\\':
            inside_quotes = not inside_quotes

    return matches

def parse_dat(dat_filepath):
    """
    Take DAT filepath as input and return parsed data in the form of
    associated arrays
    """
    if not os.path.isfile(dat_filepath):
        print("File not readable")
        return

    with open(dat_filepath, "r", encoding="utf-8") as dat_file:
        content = dat_file.read()

    header = {}
    game_data = []
    resources = {}

    matches = match_outermost_brackets(content)
    if matches:
        for data_segment in matches:
            if "clrmamepro" in content[data_segment[1] - 11: data_segment[1]] or \
                "scummvm" in content[data_segment[1] - 8: data_segment[1]]:
                header = map_key_values(data_segment[0], header)
            elif "game" in content[data_segment[1] - 5: data_segment[1]]:
                temp = {}
                temp = map_key_values(data_segment[0], temp)
                game_data.append(temp)
            elif "resource" in content[data_segment[1] - 9: data_segment[1]]:
                temp = {}
                temp = map_key_values(data_segment[0], temp)
                resources[temp["name"]] = temp
    # print(header, game_data, resources)
    return header, game_data, resources, dat_filepath

def main():
    parser = argparse.ArgumentParser(description="Process DAT files and interact with the database.")
    parser.add_argument('--upload', nargs='+', help='Upload DAT file(s) to the database')
    parser.add_argument('--match', nargs='+', help='Populate matching games in the database')
    parser.add_argument('--user', help='Username for database')
    parser.add_argument('-r', help="Recurse through directories", action='store_true')
    parser.add_argument('--skiplog', help="Skip logging dups", action='store_true')

    args = parser.parse_args()

    if args.upload:
        for filepath in args.upload:
            db_insert(parse_dat(filepath), args.user, args.skiplog)

    if args.match:
        for filepath in args.match:
            match_fileset(parse_dat(filepath), args.user)

if __name__ == "__main__":
    main()
