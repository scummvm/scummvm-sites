<?php

$servername = "localhost";
$username = "username";
$password = "password";
$dbname = "integrity";

// Create connection
$conn = new mysqli($servername, $username, $password);

// Check connection
if ($conn->connect_errno) {
  die("Connect failed: " . $conn->connect_error);
}

// Create database
$sql = "CREATE DATABASE IF NOT EXISTS " . $dbname;
if ($conn->query($sql) === TRUE) {
  echo "Database created successfully<br/>";
}
else {
  echo "Error creating database: " . $conn->error;
  exit();
}

$conn->query("USE " . $dbname);


///////////////////////// CREATE TABLES /////////////////////////

// Create engine table
$table = "CREATE TABLE IF NOT EXISTS engine (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  engineid VARCHAR(100) NOT NULL
)";

if ($conn->query($table) === TRUE) {
  echo "Table 'engine' created successfully<br/>";
}
else {
  echo "Error creating 'engine' table: " . $conn->error;
}

// Create game table
$table = "CREATE TABLE IF NOT EXISTS game (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  engine INT NOT NULL,
  gameid VARCHAR(100) NOT NULL,
  FOREIGN KEY (engine) REFERENCES engine(id)
)";

if ($conn->query($table) === TRUE) {
  echo "Table 'game' created successfully<br/>";
}
else {
  echo "Error creating 'game' table: " . $conn->error;
}

// Create file table
$table = "CREATE TABLE IF NOT EXISTS file (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  size INT NOT NULL,
  checksum VARCHAR(64) NOT NULL
)";

if ($conn->query($table) === TRUE) {
  echo "Table 'file' created successfully<br/>";
}
else {
  echo "Error creating 'file' table: " . $conn->error;
}

// Create fileset table
$table = "CREATE TABLE IF NOT EXISTS fileset (
  id INT AUTO_INCREMENT PRIMARY KEY,
  game INT NOT NULL,
  file INT NOT NULL,
  status INT,
  `key` VARCHAR(64),
  FOREIGN KEY (game) REFERENCES game(id),
  FOREIGN KEY (file) REFERENCES file(id)
)";

if ($conn->query($table) === TRUE) {
  echo "Table 'fileset' created successfully<br/>";
}
else {
  echo "Error creating 'fileset' table: " . $conn->error;
}

// Create filechecksum table
$table = "CREATE TABLE IF NOT EXISTS filechecksum (
  id INT AUTO_INCREMENT PRIMARY KEY,
  file INT NOT NULL,
  checksize INT NOT NULL,
  checktype INT NOT NULL,
  checksum VARCHAR(64) NOT NULL,
  FOREIGN KEY (file) REFERENCES file(id)
)";

if ($conn->query($table) === TRUE) {
  echo "Table 'filechecksum' created successfully<br/>";
}
else {
  echo "Error creating 'filechecksum' table: " . $conn->error;
}

// Create fileset_detection table
$table = "CREATE TABLE IF NOT EXISTS fileset_detection (
  id INT AUTO_INCREMENT PRIMARY KEY,
  fileset INT NOT NULL,
  checksum INT NOT NULL,
  FOREIGN KEY (fileset) REFERENCES fileset(id),
  FOREIGN KEY (checksum) REFERENCES filechecksum(id)
)";

if ($conn->query($table) === TRUE) {
  echo "Table 'fileset_detection' created successfully<br/>";
}
else {
  echo "Error creating 'fileset_detection' table: " . $conn->error;
}

// Create queue table
$table = "CREATE TABLE IF NOT EXISTS queue (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATETIME NOT NULL,
  notes varchar(300),
  fileset INT NOT NULL,
  ticketid INT NOT NULL,
  userid INT NOT NULL,
  commit VARCHAR(64) NOT NULL,
  FOREIGN KEY (fileset) REFERENCES fileset(id)
)";

if ($conn->query($table) === TRUE) {
  echo "Table 'queue' created successfully<br/>";
}
else {
  echo "Error creating 'queue' table: " . $conn->error;
}


$conn->close();
?>

