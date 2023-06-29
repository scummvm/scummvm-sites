<?php

$mysql_cred = json_decode(file_get_contents('mysql_config.json'), true);
$servername = "localhost";
$username = $mysql_cred["username"];
$password = $mysql_cred["password"];
$dbname = "integrity";

// Create connection
$conn = new mysqli($servername, $username, $password);

// Check connection
if ($conn->connect_errno) {
  die("Connect failed: " . $conn->connect_error);
}

$conn->query("USE " . $dbname);


///////////////////////// INSERT VALUES /////////////////////////

$query = "INSERT INTO engine (name, engineid)
VALUES ('Drascula', '1')";
$conn->query($query);
$conn->query("SET @engine_last = LAST_INSERT_ID()");

$query = "INSERT INTO game (name, engine, gameid)
VALUES ('Drascula: The Vampire Strikes Back', @engine_last, '1')";
$conn->query($query);
$conn->query("SET @game_last = LAST_INSERT_ID()");

$query = "INSERT INTO file (name, size, checksum)
VALUES ('Packet.001', '32847563', 'fac946707f07d51696a02c00cc182078')";
$conn->query($query);
$conn->query("SET @file_last = LAST_INSERT_ID()");

$query = "INSERT INTO fileset (game, file, status, `key`)
VALUES (@game_last, @file_last, 0, 'fac946707f07d51696a02c00cc182078')";
$conn->query($query);
$conn->query("SET @fileset_last = LAST_INSERT_ID()");

// Checksize: 0 (full checksum)
$query = "INSERT INTO filechecksum (file, checksize, checktype, checksum)
VALUES (@file_last, '0', 'md5', 'fac946707f07d51696a02c00cc182078')";
$conn->query($query);
$conn->query("SET @filechecksum_last = LAST_INSERT_ID()");

$query = "INSERT INTO fileset_detection (fileset, checksum)
VALUES (@fileset_last, @filechecksum_last)";
$conn->query($query);

// Checksize: 5000B
$query = "INSERT INTO filechecksum (file, checksize, checktype, checksum)
VALUES (@file_last, '5000', 'md5', 'c6a8697396e213a18472542d5f547cb4')";
$conn->query($query);
$conn->query("SET @filechecksum_last = LAST_INSERT_ID()");

$query = "INSERT INTO fileset_detection (fileset, checksum)
VALUES (@fileset_last, @filechecksum_last)";
$conn->query($query);

// Checksize: 10000B
$query = "INSERT INTO filechecksum (file, checksize, checktype, checksum)
VALUES (@file_last, '10000', 'md5', '695f4152f02b8fa4c1374a0ed04cf996')";
$conn->query($query);
$conn->query("SET @filechecksum_last = LAST_INSERT_ID()");

$query = "INSERT INTO fileset_detection (fileset, checksum)
VALUES (@fileset_last, @filechecksum_last)";
$conn->query($query);


$conn->close();
?>

