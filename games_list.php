<?php
$filename = "games_list.php";

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

echo "<ol start=\"" . $offset + 1 . "\">";
while ($row = $result->fetch_array()) {
  echo "<li>";
  echo sprintf("%s:%s-%s-%s-%s %s %s<br/>",
    $row["engineid"], $row["gameid"], $row["extra"], $row["platform"], $row["language"],
    $row["name"], $row["status"]);
  echo "</li>";
}
echo "</ol>";

if ($page > 1) {
  echo sprintf('<a href=%s>first</a>', $filename);
  echo sprintf('<a href=%s?page=%d>prev</a>', $filename, $page - 1);
}
if ($page < $num_of_pages) {
  echo sprintf('<a href=%s?page=%d>next</a>', $filename, $page + 1);
  echo sprintf('<a href=%s?page=%d>last</a>', $filename, $num_of_pages);
}
?>

