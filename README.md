# ScummVM File Integrity Check (GSoC 2025)

This repository contains the server-side code for the upcoming file integrity check for game datafiles. This repository is part of the Google Summer of Code 2025 program.

## Prerequisites
### Local

- Python 3.x
- MySQL

### Deployment
- Apache2

## Step-by-step Setup

### 1. Clone the Repository
```bash
git clone https://github.com/scummvm/scummvm-sites.git
```

### 2. Navigate to the Project Directory
```bash
cd scummvm-sites
```

### 3. Fetch All Branches
```bash
git fetch --all
```

### 4. Checkout the integrity Branch
```bash
git checkout integrity
```

### 5. Install Required Python Packages
You can also create a virtual environment (optional)
```bash
pip install -r requirements.txt
```

### 6. Install and Configure MySQL (if not already installed)
Ensure MySQL is running and properly configured.

### 7. Create the MySQL Configuration File
Create a `mysql_config.json` file with the following structure:
```json
{
  "host": "servername",
  "user": "username",
  "password": "your_password",
  "database": "db_name"
}
```
A `sample_mysql_config.json` is also present in the same directory.

### 8. Run Schema to Create Tables
```bash
python schema.py
```

## General Usecases

### 1. Manual Generation of dat files (scan.dat) from existing games collection
This utility helps in generating dat files from the existing game collections with the developers and then upload it to the database.
#### Dat File Generation :
This will generate the `.dat` file with complete checksums but no metadata.

```bash
python compute_hash.py --directory <path_to_directory> --depth 0 --size 0
```
- `--directory` : Path of directory with game files
- `--depth` : Depth from root to game directories
- `--size` : Use first n bytes of file to calculate checksum

#### Database upload (for developers ) :
Uploading the `.dat` file to the database.
```bash
python dat_parser.py --upload <scanned_dat_file/scan>.dat --user <username> --skiplog
```
- `--upload` : Upload DAT file(s) to the database
- `--match` : Populate matching games in the database
- `--user` : Username for database
- `-r` : Recurse through directories
- `--skiplog` : Skip logging dups

### 2. Uploading dat files (scummvm.dat) generated from detection entries to the DB (Initial Seeding)
Upload the `.dat` file to the database using dat_parser script -
```bash
python dat_parser.py --upload <detection_dat_file/scummvm>.dat --user <username> --skiplog
```
`scummvm.dat` can be generated using -
```bash
./scummvm --dump-all-detection-entries
```

### 3. Uploading already existing dat files (set.dat) from old collections to the DB 
Upload the `.dat` file to the database using dat_parser script -
```bash
python dat_parser.py --upload <old_dat_file/set>.dat --user <username> --skiplog
```


### 4. Validate Game Files from Client Side (integrity.json)
Make a POST request to the following endpoint:
#### Local :
```bash
http://localhost:5000/validate
```
with the body in JSON format as shown in `sample_json_request.json` present in the main directory.
There also exists a check_integrity button in the scummvm application itself which is under development.

## Deployment

The apache2 .conf file is located under `apache2-config/`.

