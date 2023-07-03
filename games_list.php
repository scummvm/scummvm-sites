<?php
$filename = "games_list.php";
$stylesheet = "style.css";
echo "<link rel='stylesheet' href='{$stylesheet}'>";

$mysql_cred = json_decode(file_get_contents('mysql_config.json'), true);
$servername = "localhost";
$username = $mysql_cred["username"];
$password = $mysql_cred["password"];
$dbname = "integrity";

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

if (!isset($_GET['page'])) {
  $page = 1;
}
else {
  $page = $_GET['page'];
}

$results_per_page = 25;
$offset = ($page - 1) * $results_per_page;
$num_of_results = $conn->query("SELECT COUNT(id) FROM game")->fetch_array()[0];
$num_of_pages = ceil($num_of_results / $results_per_page);

$query = sprintf("SELECT engineid, gameid, extra, platform, language, game.name, status
FROM game
JOIN engine ON engine.id = game.engine
JOIN fileset ON game.id = fileset.game
LIMIT %d OFFSET %d",
  $results_per_page, $offset);
$result = $conn->query($query);

echo "<table>";
echo "<th></th>";
echo "<th>engineid</th>";
echo "<th>gameid</th>";
echo "<th>extra</th>";
echo "<th>platform</th>";
echo "<th>language</th>";
echo "<th>name</th>";
echo "<th>status</th>";

$counter = $offset + 1;
while ($row = $result->fetch_array()) {
  echo "<tr>";
  echo "<td>{$counter}.</td>";
  echo "<td>{$row['engineid']}</td>";
  echo "<td>{$row['gameid']}</td>";
  echo "<td>{$row['extra']}</td>";
  echo "<td>{$row['platform']}</td>";
  echo "<td>{$row['language']}</td>";
  echo "<td>{$row['name']}</td>";
  echo "<td>{$row['status']}</td>";
  echo "</tr>";

  $counter++;
}
echo "</table>";

echo "<div class=pagination>";
if ($page > 1) {
  echo "<a href={$filename}>❮❮</a>";
  echo sprintf("<a href=%s?page=%d>❮</a>", $filename, $page - 1);
}
if ($page < $num_of_pages) {
  echo sprintf("<a href=%s?page=%d>❯</a>", $filename, $page + 1);
  echo "<a href={$filename}?page={$num_of_pages}>❯❯</a>";
}
echo "</div>";
?>

