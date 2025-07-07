import hashlib
import os
import argparse
import struct
import sys
from enum import Enum
from datetime import datetime, date
from collections import defaultdict

class FileType(Enum):
    NON_MAC = "non_mac"
    MAC_BINARY = "macbinary"
    APPLE_DOUBLE_RSRC = "apple_double_rsrc"
    APPLE_DOUBLE_MACOSX = "apple_double_macosx"
    APPLE_DOUBLE_DOT_ = "apple_double_dot_"
    RAW_RSRC = "raw_rsrc"
    ACTUAL_FORK_MAC = "actual_fork_mac"

script_version = "0.1"

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

def filesize(filepath):
    """ Returns size of file """
    return os.stat(filepath).st_size

def get_dirs_at_depth(directory, depth):
    directory = directory.rstrip(os.path.sep)
    assert os.path.isdir(directory)
    num_sep = directory.count(os.path.sep)

    for root, dirs, contents in os.walk(directory):
        num_sep_this = root.count(os.path.sep)
        if depth == num_sep_this - num_sep:
            yield root

def read_be_32(byte_stream):
    """ Return unsigned integer of size_in_bits, assuming the data is big-endian """
    (uint,) = struct.unpack(">I", byte_stream[:32//8])
    return uint

def read_be_16(byte_stream):
    """ Return unsigned integer of size_in_bits, assuming the data is big-endian """
    (uint,) = struct.unpack(">H", byte_stream[:16//8])
    return uint

def is_raw_rsrc(filepath):
    """ Returns boolean, checking if the given .rsrc file is a raw .rsrc file and not appledouble."""
    filename = os.path.basename(filepath)
    if filename.endswith(".rsrc"):
        with open(filepath, "rb") as f:
            return not is_appledouble(f.read())
    return False

def is_appledouble_rsrc(filepath):
    """ Returns boolean, checking whether the given .rsrc file is an appledouble or not."""
    filename = os.path.basename(filepath)
    if filename.endswith(".rsrc"):
        with open(filepath, "rb") as f:
            return is_appledouble(f.read())
    return False

def is_appledouble_in_dot_(filepath):
    """ Returns boolean, checking whether the given ._ file is an appledouble or not. It also checks that the parent directory is not __MACOSX as that case is handled differently """
    filename = os.path.basename(filepath)
    parent_dir = os.path.basename(os.path.dirname(filepath))
    if filename.startswith("._") and parent_dir != "__MACOSX":
        with open(filepath, "rb") as f:
            return is_appledouble(f.read())
    return False
    
def is_appledouble_in_macosx(filepath):
    """ Returns boolean, checking whether the given ._ file in __MACOSX folder is an appledouble or not. """
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
        if not header[1] and not read_be_32(header[83:]) and not read_be_32(header[87:]) and not read_be_32(header[69:]):
            return False

        checksum = crc16xmodem(header[:124])
        if checksum != read_be_16(header[124:]):
            return False

        if not header[0] and not header[74] and not header[82] and header[1] <= 63:
            # Get fork lengths
            datalen = read_be_32(header[83:])
            rsrclen = read_be_32(header[87:])

            datalen_pad = (((datalen + 127) >> 7) << 7)

            # Length check
            if (128 + datalen_pad + rsrclen <= filesize(filepath)):
                res_fork_offset = 128 + datalen_pad

            if res_fork_offset < 0:
                return False

            return True

def is_actual_resource_fork_mac(filepath):
    """ Returns boolean, checking the actual mac fork if it exists. """

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
    if (not file_byte_stream or read_be_32(file_byte_stream) != 0x00051607):
        return False

    return True

def macbin_get_resfork_data(file_byte_stream):
    """ Returns the resource fork's data section as bytes of a macbinary file as well as its size """

    if not file_byte_stream:
        return file_byte_stream

    (datalen,) = struct.unpack(">I", file_byte_stream[0x53:0x57])
    datalen_padded = ((datalen + 127) >> 7) << 7
    (rsrclen,) = struct.unpack(">I", file_byte_stream[0x57:0x5B])

    resoure_fork_offset = 128 + datalen_padded
    data_offset = int.from_bytes(file_byte_stream[resoure_fork_offset+0 : resoure_fork_offset+4])
    data_length = int.from_bytes(file_byte_stream[resoure_fork_offset+8 : resoure_fork_offset+12])

    return (file_byte_stream[resoure_fork_offset + data_offset: resoure_fork_offset + data_offset + data_length], data_length)

def macbin_get_datafork(file_byte_stream):
    if not file_byte_stream:
        return file_byte_stream

    (datalen,) = struct.unpack(">I", file_byte_stream[0x53:0x57])
    return file_byte_stream[0x80: 0x80 + datalen]

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
    if (not file_byte_stream or read_be_32(file_byte_stream) != 0x00051607):
        return False

    return True

def appledouble_get_resfork_data(file_byte_stream):
    """ Returns the resource fork's data section as bytes of an appledouble file as well as its size """
    
    entry_count = read_be_16(file_byte_stream[24:])
    for entry in range(entry_count):
        start_index = 26 + entry*12
        id = read_be_32(file_byte_stream[start_index:])
        offset = read_be_32(file_byte_stream[start_index+4:])
        length = read_be_32(file_byte_stream[start_index+8:])

        if id == 2:
            resource_fork_stream = file_byte_stream[offset:offset+length]
            data_offset = int.from_bytes(resource_fork_stream[0:4])
            data_length = int.from_bytes(resource_fork_stream[8:12])

            return (resource_fork_stream[data_offset: data_offset+data_length], data_length)

def appledouble_get_datafork(filepath, fileinfo):
    """ Returns data fork's content as bytes of appledouble file if found, otherwise empty byte string """
    try:
        index = filepath.index("__MACOSX")
    except ValueError:
        index = None

    if index is not None:
        # Remove '__MACOSX/' from filepath
        filepath = filepath[:index] + filepath[index+8+1:]
    parent_filepath = os.path.dirname(filepath)
    data_fork_path = os.path.join(parent_filepath, fileinfo[1])

    try:
        with open(data_fork_path, "rb") as f:
            return f.read()
    except (FileNotFoundError, IsADirectoryError):
        return b''

def raw_rsrc_get_datafork(filepath):
    """ Returns the data fork's content as bytes corresponding to raw rsrc file. """
    try:
        with open(filepath[:-5]+".data", "rb") as f:
            return f.read()
    except (FileNotFoundError, IsADirectoryError):
        return b''

def raw_rsrc_get_resource_fork_data(filepath):
    """ Returns the resource fork's data section as bytes of a raw rsrc file as well as its size """
    with open(filepath, "rb") as f:
        resource_fork_stream = f.read()
        data_offset = int.from_bytes(resource_fork_stream[0:4])
        data_length = int.from_bytes(resource_fork_stream[8:12])

        return (resource_fork_stream[data_offset: data_offset+data_length], data_length)

def actual_mac_fork_get_data_fork(filepath):
    """ Returns the data fork's content as bytes if the actual mac fork exists """
    try:
        with open(filepath, "rb") as f:
            return f.read()
    except (FileNotFoundError, IsADirectoryError):
        return b''

def actual_mac_fork_get_resource_fork_data(filepath):
    """ Returns the resource fork's data section as bytes of the actual mac fork as well as its size """
    resource_fork_path = os.path.join(filepath, "..namedfork", "rsrc")
    with open(resource_fork_path, "rb") as f:
        resource_fork_stream = f.read()
        data_offset = int.from_bytes(resource_fork_stream[0:4])
        data_length = int.from_bytes(resource_fork_stream[8:12])

        return (resource_fork_stream[data_offset: data_offset+data_length], data_length)

def file_checksum(filepath, alg, size, file_info):
    cur_file_size = 0
    with open(filepath, "rb") as f:
        if file_info[0] == FileType.NON_MAC:
            return (create_checksum_pairs(checksum(f, alg, size, filepath), alg, size), filesize(filepath))
        
        # Processing mac files
        res = []
        resfork = b''
        datafork = b''
        file_data = f.read()

        if file_info[0] == FileType.MAC_BINARY:
            (resfork, cur_file_size) = macbin_get_resfork_data(file_data)
            datafork = macbin_get_datafork(file_data)
        elif file_info[0] in {FileType.APPLE_DOUBLE_DOT_, FileType.APPLE_DOUBLE_RSRC, FileType.APPLE_DOUBLE_MACOSX}:
            (resfork, cur_file_size) = appledouble_get_resfork_data(file_data)
            datafork = appledouble_get_datafork(filepath, file_info)
        elif file_info[0] == FileType.RAW_RSRC:
            (resfork, cur_file_size) = raw_rsrc_get_resource_fork_data(filepath)
            datafork = raw_rsrc_get_datafork(filepath)
        elif file_info[0] == FileType.ACTUAL_FORK_MAC:
            (resfork, cur_file_size) = actual_mac_fork_get_resource_fork_data(filepath)
            datafork = actual_mac_fork_get_data_fork(filepath)

        hashes = checksum(resfork, alg, size, filepath)
        prefix = 'r'
        if len(resfork):
            res.extend(create_checksum_pairs(hashes, alg, size, prefix))

        hashes = checksum(datafork, alg, size, filepath)
        prefix = 'd'
        res.extend(create_checksum_pairs(hashes, alg, size, prefix))

        return (res, cur_file_size)

def create_checksum_pairs(hashes, alg, size, prefix=None):
    res = []

    keys = [f"{alg}", f"{alg}-5000", f"{alg}-1M", f"{alg}-t-5000"]

    if size:
        keys.append(f"{alg}-{size}")
    if prefix:
        for i, key in enumerate(keys):
            key_split = key.split('-')

            # If key is of the form "md5-t-5000"
            if (len(key_split) == 3):
                key_split[1] = f"{prefix}{key_split[1]}"
            else:
                key_split.insert(1, prefix)

            keys[i] = '-'.join(key_split)

    for i, h in enumerate(hashes):
        res.append((keys[i], h))

    return res

def checksum(file, alg, size, filepath):
    """ Returns checksum value of file buffer using a specific algoritm """
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
        hashes[2].update(bytes_stream[:1024 * 1024])
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
    """ Extracts the filename from the header of the macbinary. """
    with open(file, "rb") as f:
        header = f.read(128)
        name_len = header[1]
        filename_bytes = header[2:2+name_len]
        return filename_bytes.decode("utf-8")

def file_classification(filepath):
    """ Returns [ Filetype, Filename ]. Filetype is an enum value - NON_MAC, MAC_BINARY, APPLE_DOUBLE_RSRC, APPLE_DOUBLE_MACOSX, APPLE_DOUBLE_DOT_, RAW_RSRC
        Filename for a normal file is the same as the original. Extensions are dropped for macfiles. """

    # 1. Macbinary
    if is_macbin(filepath):
        return [FileType.MAC_BINARY, extract_macbin_filename_from_header(filepath)] 
    
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

def file_filter(files):
    """ Removes extra macfiles from the given dictionary of files that are not needed for fork calculation.
        This avoids extra checksum calculation of these mac files in form of non-mac files """
    
    to_be_deleted = []
    
    for filepath, file_info in files.items():
        # For filename.rsrc (apple double rsrc), corresponding filename file (data fork) will be removed from the files dictionary 
        if (file_info[0] == FileType.APPLE_DOUBLE_RSRC):
            parent_dir_path = os.path.dirname(filepath)
            expected_data_fork_path = os.path.join(parent_dir_path, file_info[1])
            if (expected_data_fork_path in files):
                to_be_deleted.append(expected_data_fork_path)

        # For ._filename, corresponding filename file (data fork) will be removed from the files dictionary 
        elif (file_info[0] == FileType.APPLE_DOUBLE_DOT_):
            parent_dir_path = os.path.dirname(filepath)
            expected_data_fork_path = os.path.join(parent_dir_path, file_info[1])
            if (expected_data_fork_path in files):
               to_be_deleted.append(expected_data_fork_path)

        # For ._filename, corresponding ../filename file (data fork) will be removed from the files dictionary 
        elif (file_info[0] == FileType.APPLE_DOUBLE_MACOSX):
            grand_parent_dir_path = os.path.dirname(os.path.dirname(filepath))
            expected_data_fork_path = os.path.join(grand_parent_dir_path, file_info[1])
            if (expected_data_fork_path in files):
                to_be_deleted.append(expected_data_fork_path)

        # For filename.rsrc (raw rsrc), corresponding filename.data file (data fork) and filename.finf file (finder info) will be removed from the files dictionary
        elif (file_info[0] == FileType.RAW_RSRC):
            parent_dir_path = os.path.dirname(filepath)
            expected_data_fork_path = os.path.join(parent_dir_path, file_info[1]) + ".data"
            expected_finf_path = os.path.join(parent_dir_path, file_info[1]) + ".finf"
            if (expected_data_fork_path in files):
                to_be_deleted.append(expected_data_fork_path)
            if (expected_finf_path in files):
                to_be_deleted.append(expected_finf_path)

    for file in to_be_deleted:
        del files[file]

def compute_hash_of_dirs(root_directory, depth, size=0, limit_timestamps_date=None, alg="md5"):
    """ Return dictionary containing checksums of all files in directory """
    res = []

    for directory in get_dirs_at_depth(root_directory, depth):
        hash_of_dir = dict()
        files = []
        # Dictionary with key : path and value : [ Filetype, Filename ]
        file_collection = dict()
        # Getting only files of directory and subdirectories recursively
        for root, _, contents in os.walk(directory):
            files.extend([os.path.join(root, f) for f in contents])

        # Filter out the files based on user input date - limit_timestamps_date
        filtered_file_map = filter_files_by_timestamp(files, limit_timestamp_date)

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

            if (file_info[0] == FileType.APPLE_DOUBLE_MACOSX):
                relative_dir = os.path.dirname(os.path.dirname(relative_path))
                relative_path = os.path.join(relative_dir, base_name) 

            hash_of_dir[relative_path] = file_checksum(file_path, alg, size, file_info) + (filtered_file_map[file_path],)

        res.append(hash_of_dir)
    return res


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
    raise ValueError("Invalid date format. Use YYYY, YYYY-MM, or YYYY-MM-DD")


def filter_files_by_timestamp(files, limit_timestamps_date):
    """
    Removes the files those were modified after a certain timestamp provided by the user.
    The files those were modified today are kept.
    Returns filtered map with filepath and its modification time
    """

    filtered_file_map = defaultdict(str)
    user_date = validate_date(limit_timestamps_date)
    today = date.today()

    for filepath in files:
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).date()
        if limit_timestamps_date is None or (limit_timestamps_date is not None and (mtime <= user_date or mtime == today)):
            filtered_file_map[filepath] = str(mtime)

    return filtered_file_map


def create_dat_file(hash_of_dirs, path, checksum_size=0):
    with open(f"{os.path.basename(path)}.dat", "w") as file:
        # Header
        file.writelines([
            "scummvm (\n",
            f"\tauthor scan\n",
            f"\tversion {script_version}\n",
            ")\n\n"
        ])

        # Game files
        for hash_of_dir in hash_of_dirs:
            file.write("game (\n")
            for filename, (hashes, filesize, timestamp) in hash_of_dir.items():
                data = f"name \"{filename}\" size {filesize} timestamp {timestamp}"
                for key, value in hashes:
                    data += f" {key} {value}"

                file.write(f"\trom ( {data} )\n")
            file.write(")\n\n")


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('Error: %s\n' % message)
        self.print_help()
        sys.exit(2)


parser = argparse.ArgumentParser()
parser.add_argument("--directory",
                    help="Path of directory with game files")
parser.add_argument("--depth",
                    help="Depth from root to game directories")
parser.add_argument("--size",
                    help="Use first n bytes of file to calculate checksum")
parser.add_argument("--limit-timestamps",
                    help="Format - YYYY-MM-DD or YYYY-MM or YYYY. Filters out the files those were modified after the given timestamp. Note that if the modification time is today, it would not be filtered out.")
args = parser.parse_args()
path = os.path.abspath(args.directory) if args.directory else os.getcwd()
depth = int(args.depth) if args.depth else 0
checksum_size = int(args.size) if args.size else 0
limit_timestamp_date = str(args.limit_timestamps) if args.limit_timestamps else None

create_dat_file(compute_hash_of_dirs(
    path, depth, checksum_size, limit_timestamp_date), path, checksum_size)
