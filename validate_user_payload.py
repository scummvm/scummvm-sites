import re

MAX_FILES = 10000
MAX_CHECKSUMS_PER_FILE = 8
VALID_KEYS = {"gameid", "engineid", "extra", "platform", "language", "files"}
VALID_FILE_KEYS = {"name", "size", "size-r", "size-rd", "checksums"}

# Field lengths are taken from the defined schema
FIELD_MAX_SIZES = {
    # Metadata
    "gameid": 100,
    "engineid": 100,
    "extra": 200,
    "platform": 30,
    "language": 10,
    # File
    "name": 200,
    "size": 64,
    "size-r": 64,
    "size-rd": 64,
}

"""
    Example payload - 

    {
        "gameid": "this_is_game_id",
        "engineid": "this_is_engine_id",
        "extra": "this_is_extra",
        "platform": "this_is_platform",
        "language": "lang",
        "files": [
            {
                "name": "file1",
                "size": "1234",
                "checksums": [
                                {"type": "md5", "checksum": "12345abcde12345ABCDE12345ABCDEab"}
                            ]
            }
        ]
    }
"""


def is_valid_md5(value):
    """
    Check if the md5 is 32 character long and contains [a-fA-F0-9]
    """
    if not isinstance(value, str):
        return False
    return re.fullmatch(r"[a-fA-F0-9]{32}", value) is not None


def validate_field_len(field_name, value, max_size):
    """
    General length validator for values.
    """
    if not isinstance(value, str):
        return False, f"{field_name}_invalid_type"

    if len(value) > max_size:
        return False, f"{field_name}_length_exceeded"

    return True, "valid"


def validate_user_payload(json_object):
    """
    All the checks on user data are performed here.
    - Datatype of all values
    - General structure of the payload
    - Any key missing
    - Max length of values
    - Max number of files
    - Max number of checksums per file
    - Missing filename
    - Valid numeric size
    - Valid md5 checksum
    """
    # Ensure the payload is a dictionary
    if not isinstance(json_object, dict):
        return False, "invalid_json_object"

    # Ensure any key is not missing
    missing_keys = VALID_KEYS - json_object.keys()
    if missing_keys:
        return False, f"missing_required_keys - {list(missing_keys)}"

    # Validating metadata's max length
    for key in json_object:
        if key in VALID_KEYS and key != "files":
            valid, res = validate_field_len(key, json_object[key], FIELD_MAX_SIZES[key])
            if not valid:
                return False, res

    # Ensure files are present as a list
    files = json_object.get("files", [])
    if not isinstance(files, list):
        return False, "files_should_be_list"

    # Bounds on the number of files
    if len(files) == 0:
        return False, "empty_fileset"
    if len(files) > MAX_FILES:
        return False, f"too_many_files - {len(files)}"

    # Processing every file entry
    for file_entry in files:
        if not isinstance(file_entry, dict):
            return False, "invalid_file_entry"

        # Ensure filename exist
        if "name" not in file_entry:
            return False, "missing_filename"
        # Validating file keys maximum length other than checksums
        for file_key in ["name", "size", "size-r", "size-rd"]:
            if file_key in file_entry:
                valid, res = validate_field_len(
                    file_key, file_entry[file_key], FIELD_MAX_SIZES[file_key]
                )
                if file_key.startswith("size"):
                    value = file_entry[file_key]
                    if not value.isdigit():
                        return False, f"{file_key}_not_a_number"
            if not valid:
                return False, res

        # Validation for checksums
        checksums_raw = file_entry.get("checksums", [])
        if not isinstance(checksums_raw, list):
            return False, "invalid_checksum_format: not a list"
        # Maximum number of checksums should be 8 in case of mac files.
        if len(checksums_raw) > MAX_CHECKSUMS_PER_FILE:
            return False, f"checksums_number_exceeded: {len(checksums_raw)}"

        for checksum_entry in checksums_raw:
            if not isinstance(checksum_entry, dict):
                return False, f"invalid_checksum_entry - {checksum_entry}"
            if "type" not in checksum_entry or "checksum" not in checksum_entry:
                return False, "checksum_missing_fields"
            ctype = checksum_entry["type"]
            cvalue = checksum_entry["checksum"]
            if not ctype.startswith("md5"):
                return False, f"unsupported_checksum_type: {ctype}"
            # md5 should be 32 character long and have only a-fA-F0-9
            if not is_valid_md5(cvalue):
                return False, f"invalid_md5_format: {ctype}"

        # Check if other keys than md5 are valid
        for key in file_entry:
            if key.startswith("md5"):
                continue
            if key not in VALID_FILE_KEYS:
                return False, f"invalid_file_key: {file_entry['name']} - {key}"

    return True, "valid"
