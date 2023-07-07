<?php
require 'pagination.php';

$filename = 'fileset.php';
$stylesheet = 'style.css';
$jquery_file = 'https://code.jquery.com/jquery-3.7.0.min.js';
$js_file = 'js_functions.js';
echo "<link rel='stylesheet' href='{$stylesheet}'>\n";
echo "<script type='text/javascript' src='{$jquery_file}'></script>\n";
echo "<script type='text/javascript' src='{$js_file}'></script>\n";

function get_log_page($log_id) {
  $records_per_page = 25; // FIXME: Fetch this directly from logs.php
  return intdiv($log_id, $records_per_page) + 1;
}

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

$history = $conn->query("SELECT `timestamp`, oldfileset, log
FROM history WHERE fileset = {$id}
ORDER BY `timestamp`");


// Display fileset details
echo "<h2><u>Fileset: {$id}</u></h2>";

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
  unset($result['delete']);
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
create_page($filename, 15, "file WHERE fileset = {$id}",
  "SELECT name, size, checksum, detection FROM file WHERE fileset = {$id}", "ORDER BY name");


// Dev Actions
echo "<h3>Developer Actions</h3>";
echo "<button id='delete-button' type='button' onclick='delete_id({$id})'>Mark Fileset for Deletion</button>";

if (isset($_POST['delete'])) {
  $conn->query("UPDATE fileset SET `delete` = TRUE WHERE id = {$_POST['delete']}");
  $conn->commit();
}

echo "<p id='delete-confirm' class='hidden'>Fileset marked for deletion</p>"; // Hidden


// Display history
echo "<h3>Fileset history</h3>";
if ($history->num_rows == 0) {
  echo "<p>Fileset has no history.</p>";
}
else {
  echo "<table>\n";
  echo "<th>Old ID</th>";
  echo "<th>Changed on</th>";
  echo "<th>Log ID</th>";
  while ($row = $history->fetch_assoc()) {
    $log_page = get_log_page($row['log']);
    echo "<tr>\n";
    echo "<td>{$row['oldfileset']}</td>\n";
    echo "<td>{$row['timestamp']}</td>\n";
    echo "<td><a href='logs.php?page={$log_page}'>{$row['log']}</a></td>\n";
    echo "</tr>\n";
  }
  echo "</table>\n";
}

?>

