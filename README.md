# ScummVM File Integrity Check

This repository contains the server-side code for the ScummVM's File Integrity service. 

## Web Application Access Roles
Access roles are determined by the GitHub team a user belongs to in the ScummVM organization.  
Authentication and authorization are managed via GitHub OAuth.
### Moderators
Moderators have the following permissions:
- Delete individual filesets
- Update or add fileset metadata
- Delete or update files
- Mark a fileset as a Full fileset
- Manually merge two filesets
- Log User Email Notification

### Admins
Admins inherit all moderator permissions and have additional capabilities:
- Clear the entire database
- Delete all filtered filesets in bulk

### Read-Only
Read-only users can:
- View filesets
- Compare two filesets

### No Access
All other users (not logged in or not part of any ScummVM GitHub team) have no access to the application.

## Development Setup

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
You can install dependencies using either **pip** or **uv**.
#### 5.1 Using pip
(Optional) create and activate a virtual environment, then run:
```bash
pip install -r requirements.txt
```
#### 5.2 Using UV
Make sure uv is already installed, then run:
```bash
uv sync
```
This will set up the virtual environment and install all dependencies as specified in `uv.lock`.

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
python -m src.scripts.schema
```
or using uv:
```bash
uv run -m src.scripts.schema
```
### 9. Set up .env file (includes GitHub OAuth secrets)
There is a .env.example file in the root directory. Copy it to create your .env file:
```bash
cp .env.example .env
```
Then update the values in .env as needed:
```
GITHUB_ORG=ScummVM
GITHUB_CLIENT_ID=github_client_id_from_oauth_app
GITHUB_CLIENT_SECRET=github_client_secret_from_oauth_app
FLASK_SECRET_KEY=any_random_key
```

## Deployment Guide
The Flask application is deployed using `mod_wsgi`, an Apache module for hosting WSGI applications.  
Assuming Apache and mod_wsgi are already installed:

Copy the provided Apache configuration file from the `apache2-config` directory into Apache’s `sites-available` folder:
```bash
sudo cp apache2-config/gamesdb.sev.zone.conf /etc/apache2/sites-available/
```
Enable the site:
```bash
sudo a2ensite gamesdb.sev.zone.conf
```
Reload Apache to apply changes:
```bash
sudo systemctl reload apache2
```

## CLI Script Usecases
- If using **pip**:
  - On Debian/Ubuntu (or any system where `python` points to Python 2), use:
    ```bash
    python3 -m <module>
    ```
  - Otherwise:
    ```bash
    python -m <module>
    ```
- If using **uv**:
```bash
  uv run -m <module>
```

### 1. Initial Seeding: Uploading dat files (scummvm.dat) generated from detection entries to the DB
Upload the `.dat` file to the database using dat_parser script -
```bash
python -m src.scripts.dat_parser --upload <path_to_scummvm.dat> --user <username> --skiplog
```
- `--upload` : Upload DAT file(s) to the database (seeding)
- `--match` : Populate matching games in the database
- `--user` : (Optional) Username for database
- `-r` : (Optional) Recurse through directories
- `--skiplog` : (Optional) Skip logging dups

`scummvm.dat` can be generated using -
```bash
./scummvm --dump-all-detection-entries
```

### 2. Uploading already existing dat files (set.dat) from old collections to the DB
Match the filesets from the `.dat` file using dat_parser script -
```bash
python -m src.scripts.dat_parser --match <path_to_set.dat> --user <username> --skiplog
```

### 3. Scan Utility: Manual Generation of dat files (scan.dat) from existing games collection
This utility helps in generating dat files from the existing game collections which can be uploaded to the database.

#### Dat File Generation (Scan Utility) :
This will generate the `.dat` file with complete checksums and sizes (size, size-r and size-rd in case of macfiles)

```bash
python -m src.scripts.compute_hash --directory <path_to_directory> --depth 0 --size 0 --limit-timestamps 2003-09-12
```
- `--directory` : (Required) Path of directory with game files
- `--depth` : (Optional: Default = 0) Depth from root to game directories (e.g. 0 while scanning a single directory)
- `--size` : (Optional: Default = 0) Use first n bytes of file to calculate checksum
- `--limit-timestamps` : (Optional) Format - YYYY-MM-DD or YYYY-MM or YYYY. Filters out the files those
                        were modified after the given timestamp. Note that if the
                        modification time is today, it would not be filtered out.

#### Perform Matching :
Perform matching with the exisiting filesets in database.
```bash
python -m src.scripts.dat_parser --match <scanned_dat_file/scan>.dat --user <username> --skiplog
```

## Integrity Service: Validate Game Files from Client Side
There exists a check_integrity button in the scummvm application which makes a POST request to the following endpoint:
#### Local :
```bash
http://localhost:5000/validate
```
with the request body in JSON format as shown in `sample_json_request.json` present in the root directory.

