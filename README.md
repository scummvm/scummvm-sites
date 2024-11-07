# ScummVM File Integrity Check (GSoC 2024)

This repository contains the server-side code for the upcoming file integrity check for game datafiles. This repository is part of the Google Summer of Code 2024 program.

This website needs a `mysql_config.json` in the root to run, in the form:

    {
        "servername": "<your servername>",
        "username": "<your username>",
        "password": "<your password>",
        "dbname": "<your db name>"
    }

The apache2 .conf file is located under `apache2-conf/`.
