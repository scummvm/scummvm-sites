import hashlib
import os
import argparse
import struct
import sys
from enum import Enum
from datetime import datetime, date, timedelta
from collections import defaultdict
import traceback


class FileType(Enum):
    NON_MAC = "non_mac"
    MAC_BINARY = "macbinary"
    APPLE_DOUBLE_RSRC = "apple_double_rsrc"
    APPLE_DOUBLE_MACOSX = "apple_double_macosx"
    APPLE_DOUBLE_DOT_ = "apple_double_dot_"
    RAW_RSRC = "raw_rsrc"
    ACTUAL_FORK_MAC = "actual_fork_mac"


script_version = "0.1"

SPECIAL_SYMBOLS = '/":*|\\?%<>\x7f'

# fmt: off
# CRC table
CRC16_XMODEM_TABLE = [
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
    0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
    0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
    0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
    0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
    0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
    0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
    0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
    0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
    0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
    0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
    0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
    0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
    0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
    0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
    0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
    0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
    0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
    0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
    0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
    0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
    0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
    0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
    0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
    0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
    0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
    0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
    0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
    0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
    0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
    0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
    0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0,
]


def crc16xmodem(data, crc=0):
    for byte in data:
        crc = ((crc << 8) & 0xff00) ^ CRC16_XMODEM_TABLE[(
            (crc >> 8) & 0xff) ^ byte]
    return crc & 0xffff
# fmt: on


def filesize(filepath):
    """Returns size of file"""
    return os.stat(filepath).st_size


def get_dirs_at_depth(directory, depth):
    directory = directory.rstrip(os.path.sep)
    assert os.path.isdir(directory)
    num_sep = directory.count(os.path.sep)

    for root, dirs, contents in os.walk(directory):
        num_sep_this = root.count(os.path.sep)
        if depth == num_sep_this - num_sep:
            yield root


def escape_string(s: str) -> str:
    """
    Escape strings

    Escape the following:
    - escape char: \x81
    - unallowed filename chars: https://en.wikipedia.org/wiki/Filename#Reserved_characters_and_words
    - control chars < 0x20
    """
    new_name = ""
    for char in s:
        if char == "\x81":
            new_name += "\x81\x79"
        elif char in SPECIAL_SYMBOLS or ord(char) < 0x20:
            new_name += "\x81" + chr(0x80 + ord(char))
        else:
            new_name += char
    return new_name


def encode_punycode(orig):
    """
    Punyencode strings

    - escape special characters and
    - ensure filenames can't end in a space or dotif temp == None:
    """
    s = escape_string(orig)
    encoded = s.encode("punycode").decode("ascii")
    # punyencoding adds an '-' at the end when there are no special chars
    # don't use it for comparing
    compare = encoded
    if encoded.endswith("-"):
        compare = encoded[:-1]
    if orig != compare or compare[-1] in " .":
        return "xn--" + encoded
    return orig


def punycode_need_encode(orig):
    """
    A filename needs to be punyencoded when it:

    - contains a char that should be escaped or
    - ends with a dot or a space.
    """
    if len(orig) > 4 and orig[:4] == "xn--":
        return False
    if not all((0x20 <= ord(c) < 0x80) and c not in SPECIAL_SYMBOLS for c in orig):
        return True
    if orig[-1] in " .":
        return True
    return False


def encode_path_components(filepath):
    """
    Puny encodes all separate components of filepath
    """
    parts = [i for i in filepath.split(os.sep) if i]
    encoded_parts = [
        encode_punycode(p) if punycode_need_encode(p) else p for p in parts
    ]
    return os.path.join(*encoded_parts)


def read_be_32(byte_stream, signed=False):
    """Return unsigned integer of size_in_bits, assuming the data is big-endian"""
    format = ">i" if signed else ">I"
    (uint,) = struct.unpack(format, byte_stream[: 32 // 8])
    return uint


def read_be_16(byte_stream):
    """Return unsigned integer of size_in_bits, assuming the data is big-endian"""
    (uint,) = struct.unpack(">H", byte_stream[: 16 // 8])
    return uint


def is_raw_rsrc(filepath):
    """Returns boolean, checking if the given .rsrc file is a raw .rsrc file and not appledouble."""
    filename = os.path.basename(filepath)
    if filename.endswith(".rsrc"):
        with open(filepath, "rb") as f:
            return not is_appledouble(f.read())
    return False


def is_appledouble_rsrc(filepath):
    """Returns boolean, checking whether the given .rsrc file is an appledouble or not."""
    filename = os.path.basename(filepath)
    if filename.endswith(".rsrc"):
        with open(filepath, "rb") as f:
            return is_appledouble(f.read())
    return False


def is_appledouble_in_dot_(filepath):
    """Returns boolean, checking whether the given ._ file is an appledouble or not. It also checks that the parent directory is not __MACOSX as that case is handled differently"""
    filename = os.path.basename(filepath)
    parent_dir = os.path.basename(os.path.dirname(filepath))
    if filename.startswith("._") and parent_dir != "__MACOSX":
        with open(filepath, "rb") as f:
            return is_appledouble(f.read())
    return False


def is_appledouble_in_macosx(filepath):
    """Returns boolean, checking whether the given ._ file in __MACOSX folder is an appledouble or not."""
    filename = os.path.basename(filepath)
    parent_dir = os.path.basename(os.path.dirname(filepath))
    if filename.startswith("._") and parent_dir == "__MACOSX":
        with open(filepath, "rb") as f:
            return is_appledouble(f.read())
    return False


def is_macbin(filepath):
    with open(filepath, "rb") as file:
        header = file.read(128)
        if len(header) != 128:
            return False

        res_fork_offset = -1

        # Preliminary check
        # Exclude files that have zero name len, zero data fork, zero name fork and zero type_creator.
        if (
            not header[1]
            and not read_be_32(header[83:])
            and not read_be_32(header[87:])
            and not read_be_32(header[69:])
        ):
            return False

        checksum = crc16xmodem(header[:124])
        if checksum != read_be_16(header[124:]):
            return False

        if not header[0] and not header[74] and not header[82] and header[1] <= 63:
            # Get fork lengths
            datalen = read_be_32(header[83:])
            rsrclen = read_be_32(header[87:])

            datalen_pad = ((datalen + 127) >> 7) << 7

            # Length check
            if 128 + datalen_pad + rsrclen <= filesize(filepath):
                res_fork_offset = 128 + datalen_pad

            if res_fork_offset < 0:
                return False

            return True


def is_actual_resource_fork_mac(filepath):
    """Returns boolean, checking the actual mac fork if it exists."""

    resource_fork_path = os.path.join(filepath, "..namedfork", "rsrc")
    return os.path.exists(resource_fork_path)


def is_appledouble(file_byte_stream):
    """
    Appledouble Structure -

    Header:
    +$00 / 4: signature (0x00 0x05 0x16 0x00)
    +$04 / 4: version (0x00 0x01 0x00 0x00 (v1) -or- 0x00 0x02 0x00 0x00 (v2))
    +$08 /16: home file system string (v1) -or- zeroes (v2)
    +$18 / 2: number of entries

    Entries:
    +$00 / 4: entry ID (1-15)
    +$04 / 4: offset to data from start of file
    +$08 / 4: length of entry in bytes; may be zero
    """
    if not file_byte_stream or read_be_32(file_byte_stream) != 0x00051607:
        return False

    return True


def macbin_get_resfork_data(file_byte_stream):
    """Returns the resource fork's data section as bytes, data fork size (size), resource fork size (size-r) and data section of resource fork size (size-rd) of a macbinary file"""

    if not file_byte_stream:
        return file_byte_stream

    (datalen,) = struct.unpack(">I", file_byte_stream[0x53:0x57])
    datalen_padded = ((datalen + 127) >> 7) << 7
    (rsrclen,) = struct.unpack(">I", file_byte_stream[0x57:0x5B])

    resoure_fork_offset = 128 + datalen_padded
    rd_offset = int.from_bytes(
        file_byte_stream[resoure_fork_offset + 0 : resoure_fork_offset + 4]
    )
    rd_length = int.from_bytes(
        file_byte_stream[resoure_fork_offset + 8 : resoure_fork_offset + 12]
    )

    return (
        file_byte_stream[
            resoure_fork_offset + rd_offset : resoure_fork_offset
            + rd_offset
            + rd_length
        ],
        datalen,
        rsrclen,
        rd_length,
    )


def macbin_get_datafork(file_byte_stream):
    if not file_byte_stream:
        return file_byte_stream

    (datalen,) = struct.unpack(">I", file_byte_stream[0x53:0x57])
    return file_byte_stream[0x80 : 0x80 + datalen]


def appledouble_get_resfork_data(file_byte_stream):
    """Returns the resource fork's data section as bytes, size of resource fork (size-r) and size of data section of resource fork (size-rd) of an appledouble file"""

    entry_count = read_be_16(file_byte_stream[24:])
    for entry in range(entry_count):
        start_index = 26 + entry * 12
        id = read_be_32(file_byte_stream[start_index:])
        offset = read_be_32(file_byte_stream[start_index + 4 :])
        length = read_be_32(file_byte_stream[start_index + 8 :])

        if id == 2:
            resource_fork_stream = file_byte_stream[offset : offset + length]
            rd_offset = int.from_bytes(resource_fork_stream[0:4])
            rd_length = int.from_bytes(resource_fork_stream[8:12])

            return (
                resource_fork_stream[rd_offset : rd_offset + rd_length],
                length,
                rd_length,
            )


def appledouble_get_datafork(filepath, fileinfo):
    """Returns data fork's content as bytes and size of data fork of an appledouble file."""
    try:
        index = filepath.index("__MACOSX")
    except ValueError:
        index = None

    if index is not None:
        # Remove '__MACOSX/' from filepath
        filepath = filepath[:index] + filepath[index + 8 + 1 :]
    parent_filepath = os.path.dirname(filepath)
    data_fork_path = os.path.join(parent_filepath, fileinfo[1])

    try:
        with open(data_fork_path, "rb") as f:
            data = f.read()
            return (data, len(data))
    except (FileNotFoundError, IsADirectoryError) as e:
        raise e


def raw_rsrc_get_datafork(filepath):
    """Returns the data fork's content as bytes and size of the data fork corresponding to raw rsrc file."""
    try:
        with open(filepath[:-5] + ".data", "rb") as f:
            data = f.read()
            return (data, len(data))
    except (FileNotFoundError, IsADirectoryError) as e:
        raise e


def raw_rsrc_get_resource_fork_data(filepath):
    """Returns the resource fork's data section as bytes, size of resource fork (size-r) and size of data section of resource fork (size-rd) of a raw rsrc file."""
    with open(filepath, "rb") as f:
        resource_fork_stream = f.read()
        resource_fork_len = len(resource_fork_stream)
        rd_offset = int.from_bytes(resource_fork_stream[0:4])
        rd_length = int.from_bytes(resource_fork_stream[8:12])

        return (
            resource_fork_stream[rd_offset : rd_offset + rd_length],
            resource_fork_len,
            rd_length,
        )


def actual_mac_fork_get_data_fork(filepath):
    """Returns the data fork's content as bytes and its size if the actual mac fork exists"""
    try:
        with open(filepath, "rb") as f:
            data = f.read()
            return (data, len(data))
    except (FileNotFoundError, IsADirectoryError) as e:
        raise e


def actual_mac_fork_get_resource_fork_data(filepath):
    """Returns the resource fork's data section as bytes, size of resource fork (size-r) and size of data section of resource fork (size-rd) of the actual mac fork."""
    resource_fork_path = os.path.join(filepath, "..namedfork", "rsrc")
    with open(resource_fork_path, "rb") as f:
        resource_fork_stream = f.read()
        resource_fork_len = len(resource_fork_stream)
        rd_offset = int.from_bytes(resource_fork_stream[0:4])
        rd_length = int.from_bytes(resource_fork_stream[8:12])

        return (
            resource_fork_stream[rd_offset : rd_offset + rd_length],
            resource_fork_len,
            rd_length,
        )


def file_checksum(filepath, alg, custom_checksum_size, file_info):
    with open(filepath, "rb") as f:
        if file_info[0] == FileType.NON_MAC:
            return (
                create_checksum_pairs(
                    checksum(f, alg, custom_checksum_size, filepath),
                    alg,
                    custom_checksum_size,
                ),
                filesize(filepath),
                0,
                0,
            )

        # Processing mac files
        res = []
        resfork = b""
        datafork = b""
        file_data = f.read()

        size = 0
        size_r = 0
        size_rd = 0

        if file_info[0] == FileType.MAC_BINARY:
            (resfork, size, size_r, size_rd) = macbin_get_resfork_data(file_data)
            datafork = macbin_get_datafork(file_data)
        elif file_info[0] in {
            FileType.APPLE_DOUBLE_DOT_,
            FileType.APPLE_DOUBLE_RSRC,
            FileType.APPLE_DOUBLE_MACOSX,
        }:
            (resfork, size_r, size_rd) = appledouble_get_resfork_data(file_data)
            (datafork, size) = appledouble_get_datafork(filepath, file_info)
        elif file_info[0] == FileType.RAW_RSRC:
            (resfork, size_r, size_rd) = raw_rsrc_get_resource_fork_data(filepath)
            datafork, size = raw_rsrc_get_datafork(filepath)
        elif file_info[0] == FileType.ACTUAL_FORK_MAC:
            (resfork, size_r, size_rd) = actual_mac_fork_get_resource_fork_data(
                filepath
            )
            (datafork, size) = actual_mac_fork_get_data_fork(filepath)

        hashes = checksum(resfork, alg, custom_checksum_size, filepath)
        prefix = "r"
        if len(resfork):
            res.extend(create_checksum_pairs(hashes, alg, custom_checksum_size, prefix))

        hashes = checksum(datafork, alg, custom_checksum_size, filepath)
        prefix = "d"
        res.extend(create_checksum_pairs(hashes, alg, custom_checksum_size, prefix))

        return (res, size, size_r, size_rd)


def create_checksum_pairs(hashes, alg, size, prefix=None):
    res = []

    keys = [f"{alg}", f"{alg}-5000", f"{alg}-1M", f"{alg}-t-5000"]

    if size:
        keys.append(f"{alg}-{size}")
    if prefix:
        for i, key in enumerate(keys):
            key_split = key.split("-")

            # If key is of the form "md5-t-5000"
            if len(key_split) == 3:
                key_split[1] = f"{prefix}{key_split[1]}"
            else:
                key_split.insert(1, prefix)

            keys[i] = "-".join(key_split)

    for i, h in enumerate(hashes):
        res.append((keys[i], h))

    return res


def checksum(file, alg, size, filepath):
    """Returns checksum value of file buffer using a specific algoritm"""
    # Will contain 5 elements:
    #  - Full size checksum
    #  - Checksum of first 5000B
    #  - Checksum of first 1MB
    #  - Checksum of last 5000B (tail)
    #  - Checksum of first *size* bytes
    hashes = []

    if alg == "md5":
        hashes = [hashlib.md5() for _ in range(5)]
    elif alg == "sha1":
        hashes = [hashlib.sha1() for _ in range(5)]
    elif alg == "sha256":
        hashes = [hashlib.sha256() for _ in range(5)]

    # If file is not a MacBinary
    if not isinstance(file, bytes):
        # Read file in 8MB chunks for full checksum
        for byte_block in iter(lambda: file.read(8 * 1024 * 1024), b""):
            hashes[0].update(byte_block)

        # First 5000B
        file.seek(0)
        hashes[1].update(file.read(5000))

        # First 1MB
        file.seek(0)
        hashes[2].update(file.read(1024 * 1024))

        # Last 5000B
        if filesize(filepath) >= 5000:
            file.seek(-5000, os.SEEK_END)
            hashes[3].update(file.read())
        else:
            hashes[3] = hashes[0]

        # Custom size; may be None
        # Size is in bytes
        # Reads entire required size at once, inefficient for large sizes
        if size and size <= filesize(filepath):
            file.seek(0)
            hashes[4].update(file.read(size))
        else:
            hashes[4] = None
    else:
        bytes_stream = file

        hashes[0].update(bytes_stream)
        hashes[1].update(bytes_stream[:5000])
        hashes[2].update(bytes_stream[: 1024 * 1024])
        if len(bytes_stream) >= 5000:
            hashes[3].update(bytes_stream[-5000:])
        else:
            hashes[3] = hashes[0]

        # Custom size
        if size and size <= filesize(filepath):
            hashes[4].update(bytes_stream[:size])
        else:
            hashes[4] = None

    hashes = [h.hexdigest() for h in hashes if h]
    return hashes


def extract_macbin_filename_from_header(file):
    """Extracts the filename from the header of the macbinary."""
    with open(file, "rb") as f:
        header = f.read(128)
        name_len = header[1]
        filename_bytes = header[2 : 2 + name_len]
        filename = filename_bytes.decode("mac_roman")
        return filename


def file_classification(filepath):
    """Returns [ Filetype, Filename ]. Filetype is an enum value - NON_MAC, MAC_BINARY, APPLE_DOUBLE_RSRC, APPLE_DOUBLE_MACOSX, APPLE_DOUBLE_DOT_, RAW_RSRC
    Filename for a normal file is the same as the original. Extensions are dropped for macfiles."""
    try:
        # 1. Macbinary
        if is_macbin(filepath):
            base_name = extract_macbin_filename_from_header(filepath)
            return [FileType.MAC_BINARY, base_name]

        # 2. Appledouble .rsrc
        if is_appledouble_rsrc(filepath):
            base_name, _ = os.path.splitext(os.path.basename(filepath))
            return [FileType.APPLE_DOUBLE_RSRC, base_name]

        # 3. Raw .rsrc
        if is_raw_rsrc(filepath):
            base_name, _ = os.path.splitext(os.path.basename(filepath))
            return [FileType.RAW_RSRC, base_name]

        # 4. Appledouble in ._
        if is_appledouble_in_dot_(filepath):
            filename = os.path.basename(filepath)
            actual_filename = filename[2:]
            return [FileType.APPLE_DOUBLE_DOT_, actual_filename]

        # 5. Appledouble in __MACOSX folder
        if is_appledouble_in_macosx(filepath):
            filename = os.path.basename(filepath)
            actual_filename = filename[2:]
            return [FileType.APPLE_DOUBLE_MACOSX, actual_filename]

        # 6. Actual resource fork of mac
        if is_actual_resource_fork_mac(filepath):
            filename = os.path.basename(filepath)
            return [FileType.ACTUAL_FORK_MAC, filename]

        # Normal file
        else:
            return [FileType.NON_MAC, os.path.basename(filepath)]
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except OSError as e:
        raise OSError(f"Could not read file: {filepath}") from e


def file_filter(files):
    """Removes extra macfiles from the given dictionary of files that are not needed for fork calculation.
    This avoids extra checksum calculation of these mac files in form of non-mac files"""

    to_be_deleted = []

    for filepath, file_info in files.items():
        # For filename.rsrc (apple double rsrc), corresponding filename file (data fork) will be removed from the files dictionary
        if file_info[0] == FileType.APPLE_DOUBLE_RSRC:
            parent_dir_path = os.path.dirname(filepath)
            expected_data_fork_path = os.path.join(parent_dir_path, file_info[1])
            if expected_data_fork_path in files:
                to_be_deleted.append(expected_data_fork_path)

        # For ._filename, corresponding filename file (data fork) will be removed from the files dictionary
        elif file_info[0] == FileType.APPLE_DOUBLE_DOT_:
            parent_dir_path = os.path.dirname(filepath)
            expected_data_fork_path = os.path.join(parent_dir_path, file_info[1])
            if expected_data_fork_path in files:
                to_be_deleted.append(expected_data_fork_path)

        # For ._filename, corresponding ../filename file (data fork) will be removed from the files dictionary
        elif file_info[0] == FileType.APPLE_DOUBLE_MACOSX:
            grand_parent_dir_path = os.path.dirname(os.path.dirname(filepath))
            expected_data_fork_path = os.path.join(grand_parent_dir_path, file_info[1])
            if expected_data_fork_path in files:
                to_be_deleted.append(expected_data_fork_path)

        # For filename.rsrc (raw rsrc), corresponding filename.data file (data fork) and filename.finf file (finder info) will be removed from the files dictionary
        elif file_info[0] == FileType.RAW_RSRC:
            parent_dir_path = os.path.dirname(filepath)
            expected_data_fork_path = (
                os.path.join(parent_dir_path, file_info[1]) + ".data"
            )
            expected_finf_path = os.path.join(parent_dir_path, file_info[1]) + ".finf"
            if expected_data_fork_path in files:
                to_be_deleted.append(expected_data_fork_path)
            if expected_finf_path in files:
                to_be_deleted.append(expected_finf_path)

    for file in to_be_deleted:
        del files[file]


def compute_hash_of_dirs(
    root_directory, depth, size=0, limit_timestamps_date=None, alg="md5"
):
    """Return dictionary containing checksums of all files in directory"""
    res = []

    for directory in get_dirs_at_depth(root_directory, depth):
        try:
            hash_of_dir = dict()
            files = []
            # Dictionary with key : path and value : [ Filetype, Filename ]
            file_collection = dict()
            # Getting only files of directory and subdirectories recursively
            for root, _, contents in os.walk(directory):
                files.extend([os.path.join(root, f) for f in contents])

            # Filter out the files based on user input date - limit_timestamps_date
            filtered_file_map = filter_files_by_timestamp(files, limit_timestamps_date)

            # Produce filetype and filename(name to be used in game entry) for each file
            for filepath in filtered_file_map:
                file_collection[filepath] = file_classification(filepath)

            # Remove extra entries of macfiles to avoid extra checksum calculation in form of non mac files
            # Checksum for both the forks are calculated using a single file, so other files should be removed from the collection
            file_filter(file_collection)

            # Calculate checksum of files
            for file_path, file_info in file_collection.items():
                # relative_path is used for the name field in game entry
                relative_path = os.path.relpath(file_path, directory)
                base_name = file_info[1]
                relative_dir = os.path.dirname(relative_path)
                relative_path = os.path.join(relative_dir, base_name)

                if file_info[0] == FileType.APPLE_DOUBLE_MACOSX:
                    relative_dir = os.path.dirname(os.path.dirname(relative_path))
                    relative_path = os.path.join(relative_dir, base_name)

                hash_of_dir[relative_path] = file_checksum(
                    file_path, alg, size, file_info
                ) + (filtered_file_map[file_path], os.path.basename(directory))

            res.append(hash_of_dir)
        except Exception:
            print(f"Error: Could not process the given directory: {directory}.")
            raise
    return res


def extract_macbin_mtime(file_byte_stream):
    """
    Returns modification time of macbinary file from the header.
    Doc - +$5f / 4: modification date/time.
    Doc - Timestamps are unsigned 32-bit values indicating the time in seconds since midnight on Jan 1, 1904, in local time.
    """
    macbin_epoch = datetime(1904, 1, 1)
    header = file_byte_stream[:128]
    macbin_seconds = read_be_32(header[0x5F:])
    return (macbin_epoch + timedelta(seconds=macbin_seconds)).date()


def extract_mtime_appledouble(file_byte_stream):
    """
     Returns modification time of appledouble file.
     Doc 1 - The File Dates Info entry (ID=8) consists of the file creation, modification, backup
     and access times (see Figure 2-1), stored as a signed number of seconds before
     or after 12:00 a.m. (midnight), January 1, 2000 Greenwich Mean Time (GMT)

     Doc 2 -
     struct ASFileDates  /* entry ID 8, file dates info */
    {
        sint32 create; /* file creation date/time */
        sint32 modify; /* last modification date/time */
        sint32 backup; /* last backup date/time */
        sint32 access; /* last access date/time */
    }; /* ASFileDates */
    """
    entry_count = read_be_16(file_byte_stream[24:])
    for entry in range(entry_count):
        start_index = 26 + entry * 12
        id = read_be_32(file_byte_stream[start_index:])
        offset = read_be_32(file_byte_stream[start_index + 4 :])
        length = read_be_32(file_byte_stream[start_index + 8 :])

        if id == 8:
            date_info_data = file_byte_stream[offset : offset + length]
            if len(date_info_data) < 16:
                raise ValueError("Error: FileDatesInfo block is too short.")
            appledouble_epoch = datetime(2000, 1, 1)
            modify_seconds = read_be_32(date_info_data[4:8], signed=True)
            return (appledouble_epoch + timedelta(seconds=modify_seconds)).date()

    return None


def macfile_timestamp(filepath):
    """
    Returns the modification times for the mac file from their finderinfo.
    If the file is not a macfile, it returns None
    """
    try:
        with open(filepath, "rb") as f:
            data = f.read()
            # Macbinary
            if is_macbin(filepath):
                return extract_macbin_mtime(data)

            # Appledouble
            if (
                is_appledouble_rsrc(filepath)
                or is_appledouble_in_dot_(filepath)
                or is_appledouble_in_macosx(filepath)
            ):
                return extract_mtime_appledouble(data)

        return None
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except OSError as e:
        raise OSError(f"Could not read file: {filepath}") from e
    except ValueError as e:
        raise e


def validate_date(date_str):
    """
    Confirms if the user provided timestamp is in a valid format.
    Returns the date as a datetime object.
    """
    formats = ["%Y-%m-%d", "%Y-%m", "%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(
        f"Error: Invalid date format: {date_str}. Use YYYY, YYYY-MM, or YYYY-MM-DD"
    )


def filter_files_by_timestamp(files, limit_timestamps_date):
    """
    Removes the files those were modified after a certain timestamp provided by the user.
    The files those were modified today are kept.
    Returns filtered map with filepath and its modification time
    """

    filtered_file_map = defaultdict(str)

    if limit_timestamps_date is not None:
        user_date = limit_timestamps_date
    today = date.today()

    for filepath in files:
        mtime = macfile_timestamp(filepath)
        if mtime is None:
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).date()
        if limit_timestamps_date is None or (
            limit_timestamps_date is not None and (mtime <= user_date or mtime == today)
        ):
            filtered_file_map[filepath] = str(mtime)

    return filtered_file_map


def create_dat_file(hash_of_dirs, path, checksum_size=0):
    with open(f"{os.path.basename(path)}.dat", "w") as file:
        # Header
        file.writelines(
            [
                "scummvm (\n",
                "\tauthor scan\n",
                f"\tversion {script_version}\n",
                ")\n\n",
            ]
        )

        # Game files
        for hash_of_dir in hash_of_dirs:
            file.write("game (\n")
            path_added = False
            for filename, (
                hashes,
                size,
                size_r,
                size_rd,
                timestamp,
                relative_path,
            ) in hash_of_dir.items():
                if not path_added:
                    file.write(f"\tdata_path {relative_path}\n")
                    path_added = True
                filename = encode_path_components(filename)
                data = f"""name "{filename}" size {size} size-r {size_r} size-rd {size_rd} modification-time {timestamp}"""
                for key, value in hashes:
                    data += f" {key} {value}"

                file.write(f"\trom ( {data} )\n")
            file.write(")\n\n")


def parse_positive_int(value, name):
    """
    Parser the size and depth values passed as cli arguements.
    """
    try:
        num = int(value) if value else 0
    except ValueError:
        print(f"Error: Invalid {name} argument: {value}")
        sys.exit(1)
    if num < 0:
        print(
            f"Error: Invalid {name} value: {num}. Use a value greater than or equal to 0."
        )
        sys.exit(1)
    return num


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write("Error: %s\n" % message)
        self.print_help()
        sys.exit(2)


def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--directory", required=True, help="Path of directory with game files"
        )
        parser.add_argument("--depth", help="Depth from root to game directories")
        parser.add_argument(
            "--size", help="Use first n bytes of file to calculate checksum"
        )
        parser.add_argument(
            "--limit-timestamps",
            help="Format - YYYY-MM-DD or YYYY-MM or YYYY. Filters out the files those were modified after the given timestamp. Note that if the modification time is today, it would not be filtered out.",
        )

        args = parser.parse_args()
        path = args.directory
        if not os.path.isdir(path):
            print(f"Error: Directory does not exist: {path}.")
            sys.exit(1)
        path = os.path.abspath(path)

        depth = parse_positive_int(args.depth, "depth")
        checksum_size = parse_positive_int(args.size, "size")

        limit_timestamps_date = None
        try:
            if args.limit_timestamps:
                limit_timestamps_date = validate_date(str(args.limit_timestamps))
        except ValueError as ve:
            print(ve)
            sys.exit(1)

        create_dat_file(
            compute_hash_of_dirs(path, depth, checksum_size, limit_timestamps_date),
            path,
            checksum_size,
        )
    except KeyboardInterrupt:
        print("Operation cancelled by user")
        sys.exit(0)
    except Exception:
        traceback.print_exc()
        print(
            "Could not handle the exception. Look through the traceback and open an issue at: https://github.com/scummvm/scummvm-sites/issues"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
