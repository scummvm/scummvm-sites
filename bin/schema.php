<?php

$mysql_cred = json_decode(file_get_contents('mysql_config.json'), true);
$servername = $mysql_cred["servername"];
$username = $mysql_cred["username"];
$password = $mysql_cred["password"];
$dbname = $mysql_cred["dbname"];

// Create connection
$conn = new mysqli($servername, $username, $password);

// Check connection
if ($conn->connect_errno) {
  die("Connect failed: " . $conn->connect_error);
}

// Create database
$sql = "CREATE DATABASE IF NOT EXISTS " . $dbname;
if ($conn->query($sql) === TRUE) {
  echo "Database created successfully\n";
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
  name VARCHAR(200),
  engineid VARCHAR(100) NOT NULL
)";

if ($conn->query($table) === TRUE) {
  echo "Table 'engine' created successfully\n";
}
else {
  echo "Error creating 'engine' table: " . $conn->error;
}

// Create game table
$table = "CREATE TABLE IF NOT EXISTS game (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200),
  engine INT NOT NULL,
  gameid VARCHAR(100) NOT NULL,
  extra VARCHAR(200),
  platform VARCHAR(30),
  language VARCHAR(10),
  FOREIGN KEY (engine) REFERENCES engine(id)
)";

if ($conn->query($table) === TRUE) {
  echo "Table 'game' created successfully\n";
}
else {
  echo "Error creating 'game' table: " . $conn->error;
}

// Create fileset table
$table = "CREATE TABLE IF NOT EXISTS fileset (
  id INT AUTO_INCREMENT PRIMARY KEY,
  game INT,
  status VARCHAR(20),
  src VARCHAR(20),
  `key` VARCHAR(64),
  `megakey` VARCHAR(64),
  `delete` BOOLEAN DEFAULT FALSE NOT NULL,
  `timestamp` TIMESTAMP NOT NULL,
  detection_size INT,
  FOREIGN KEY (game) REFERENCES game(id)
)";

if ($conn->query($table) === TRUE) {
  echo "Table 'fileset' created successfully\n";
}
else {
  echo "Error creating 'fileset' table: " . $conn->error;
}

// Create file table
$table = "CREATE TABLE IF NOT EXISTS file (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  size BIGINT NOT NULL,
  checksum VARCHAR(64) NOT NULL,
  fileset INT NOT NULL,
  detection BOOLEAN NOT NULL,
  FOREIGN KEY (fileset) REFERENCES fileset(id) ON DELETE CASCADE
)";

if ($conn->query($table) === TRUE) {
  echo "Table 'file' created successfully\n";
}
else {
  echo "Error creating 'file' table: " . $conn->error;
}

// Create filechecksum table
$table = "CREATE TABLE IF NOT EXISTS filechecksum (
  id INT AUTO_INCREMENT PRIMARY KEY,
  file INT NOT NULL,
  checksize VARCHAR(10) NOT NULL,
  checktype VARCHAR(10) NOT NULL,
  checksum VARCHAR(64) NOT NULL,
  FOREIGN KEY (file) REFERENCES file(id) ON DELETE CASCADE
)";

if ($conn->query($table) === TRUE) {
  echo "Table 'filechecksum' created successfully\n";
}
else {
  echo "Error creating 'filechecksum' table: " . $conn->error;
}

// Create queue table
$table = "CREATE TABLE IF NOT EXISTS queue (
  id INT AUTO_INCREMENT PRIMARY KEY,
  time TIMESTAMP NOT NULL,
  notes varchar(300),
  fileset INT,
  userid INT NOT NULL,
  commit VARCHAR(64) NOT NULL,
  FOREIGN KEY (fileset) REFERENCES fileset(id)
)";

if ($conn->query($table) === TRUE) {
  echo "Table 'queue' created successfully\n";
}
else {
  echo "Error creating 'queue' table: " . $conn->error;
}

// Create log table
$table = "CREATE TABLE IF NOT EXISTS log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  `timestamp` TIMESTAMP NOT NULL,
  category VARCHAR(100) NOT NULL,
  user VARCHAR(100) NOT NULL,
  `text` varchar(300)
)";

if ($conn->query($table) === TRUE) {
  echo "Table 'log' created successfully\n";
}
else {
  echo "Error creating 'log' table: " . $conn->error;
}

// Create history table
$table = "CREATE TABLE IF NOT EXISTS history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  `timestamp` TIMESTAMP NOT NULL,
  fileset INT NOT NULL,
  oldfileset INT NOT NULL,
  log INT
)";

if ($conn->query($table) === TRUE) {
  echo "Table 'history' created successfully\n";
}
else {
  echo "Error creating 'history' table: " . $conn->error;
}

// Create transactions table
$table = "CREATE TABLE IF NOT EXISTS transactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  `transaction` INT NOT NULL,
  fileset INT NOT NULL
)";

if ($conn->query($table) === TRUE) {
  echo "Table 'transactions' created successfully\n";
}
else {
  echo "Error creating 'transactions' table: " . $conn->error;
}


///////////////////////// CREATE INDEX /////////////////////////

// Create indices for fast data retrieval
// PK and FK are automatically indexed in InnoDB, so they are not included
$index = "CREATE INDEX detection ON file (detection)";

if ($conn->query($index) === TRUE) {
  echo "Created index for 'file.detection'\n";
}
else {
  echo "Error creating index for 'file.detection': " . $conn->error;
}

$index = "CREATE INDEX checksum ON filechecksum (checksum)";

if ($conn->query($index) === TRUE) {
  echo "Created index for 'filechecksum.checksum'\n";
}
else {
  echo "Error creating index for 'filechecksum.checksum': " . $conn->error;
}

$index = "CREATE INDEX engineid ON engine (engineid)";

if ($conn->query($index) === TRUE) {
  echo "Created index for 'engine.engineid'\n";
}
else {
  echo "Error creating index for 'engine.engineid': " . $conn->error;
}

$index = "CREATE INDEX fileset_key ON fileset (`key`)";

if ($conn->query($index) === TRUE) {
  echo "Created index for 'fileset.key'\n";
}
else {
  echo "Error creating index for 'fileset.key': " . $conn->error;
}

$index = "CREATE INDEX status ON fileset (status)";

if ($conn->query($index) === TRUE) {
  echo "Created index for 'fileset.status'\n";
}
else {
  echo "Error creating index for 'fileset.status': " . $conn->error;
}

$index = "CREATE INDEX fileset ON history (fileset)";

if ($conn->query($index) === TRUE) {
  echo "Created index for 'history.fileset'\n";
}
else {
  echo "Error creating index for 'history.fileset': " . $conn->error;
}

$conn->close();
?>
