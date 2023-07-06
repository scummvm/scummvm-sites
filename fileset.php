<?php
$stylesheet = "style.css";
echo "<link rel='stylesheet' href='{$stylesheet}'>\n";

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
  if ($conn->query("SELECT id FROM fileset WHERE id = {$id}")->num_rows == 0)
    $id = $conn->query("SELECT fileset FROM history WHERE oldfileset = {$id}")->fetch_array()[0];
}

// Display history
$history = $conn->query("SELECT `timestamp`, oldfileset
FROM history WHERE fileset = {$id}
ORDER BY `timestamp`");

// Display fileset details
$result = $conn->query("SELECT * FROM fileset WHERE id = {$id}")->fetch_assoc();

echo "<h3>Fileset details</h3>";
echo "<table>\n";
if ($result['game']) {
  $temp = $conn->query("SELECT game.name as 'game name', engineid, gameid, extra, platform, language
FROM fileset JOIN game ON game.id = fileset.game JOIN engine ON engine.id = game.engine
WHERE fileset.id = {$id}");
  $result = array_merge($result, $temp->fetch_assoc());
}
else {
  unset($result['key']);
  unset($result['status']);
}

foreach (array_keys($result) as $column) {
  if ($column == 'id' || $column == 'game')
    continue;

  echo "<th>{$column}</th>\n";
}

echo "<tr>\n";
foreach ($result as $column => $value) {
  if ($column == 'id' || $column == 'game')
    continue;

  echo "<td>{$value}</td>";
}
echo "</tr>\n";
echo "</table>\n";

echo "<h3>Files in the fileset</h3>";
echo "<table>\n";
$res = $conn->query("SELECT * from file WHERE fileset = {$id}");
$first_row = true;
while ($row = $res->fetch_assoc()) {
  if ($first_row) { // If it is the first run
    foreach (array_keys($row) as $column) {
      if ($column == 'id')
        continue;

      echo "<th>{$column}</th>\n";
    }
    $first_row = false;
  }

  echo "<tr>\n";
  foreach ($row as $column => $value) {
    if ($column == 'id')
      continue;

    echo "<td>{$value}</td>";
  }
  echo "</tr>\n";
}
echo "</table>\n";

if ($history->num_rows == 0) {
  echo "Fileset has no history.";
}
else {
  echo "<h3>Fileset history</h3>";
  echo "<table>\n";
  echo "<th>Old ID</th>";
  echo "<th>Changed on</th>";
  while ($row = $history->fetch_assoc()) {
    echo "<tr>\n";
    echo "<td>{$row['oldfileset']}</td>\n";
    echo "<td>{$row['timestamp']}</td>\n";
    echo "</tr>\n";
  }
  echo "</table>\n";
}

?>

