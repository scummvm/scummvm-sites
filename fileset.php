<?php

$mysql_cred = json_decode(file_get_contents('mysql_config.json'), true);
$servername = $mysql_cred["servername"];
$username = $mysql_cred["username"];
$password = $mysql_cred["password"];
$dbname = $mysql_cred["dbname"];

// Create connection
mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
$conn = new mysqli($servername, $username, $password);
$conn->set_charset('utf8mb4');
$conn->autocommit(FALSE);

// Check connection
if ($conn->connect_errno) {
  die("Connect failed: " . $conn->connect_error);
}

$conn->query("USE " . $dbname);

if (!isset($_GET['id'])) {
  $id = 1;
}
else {
  $max_id = $conn->query("SELECT MAX(id) FROM fileset")->fetch_array()[0];
  $id = max(1, min($_GET['id'], $max_id));
}

// Display history
$res = $conn->query("SELECT `timestamp`, oldfileset
FROM history WHERE fileset = {$id}
ORDER BY `timestamp`")->fetch_all();

if (count($res) == 0) {
  echo "Fileset has no history.";
}
else {
  echo "This fileset was merged with the following filesets in chronological order: ";
  foreach ($res as $history) {
    echo "{$history[1]}, ";
  }
}

?>

