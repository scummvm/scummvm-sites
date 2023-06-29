<?php
$filename = "index.php";

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

$query = sprintf("SELECT name, extra, platform, language FROM game LIMIT %d OFFSET %d",
  $results_per_page, $offset);
$result = $conn->query($query);

echo "<ol start=\"" . $offset + 1 . "\">";
while ($row = $result->fetch_array()) {
  echo "<li>";
  echo sprintf("%s (%s, %s, %s)<br/>", $row["name"], $row["extra"], $row["platform"], $row["language"]);
  echo "</li>";
}
echo "</ol>";

echo '<a href =' . $filename . '"?page=1">first</a>';
if ($page > 1)
  echo '<a href =' . $filename . '"?page=' . $page - 1 . '">prev</a>';
if ($page < $num_of_pages)
  echo '<a href =' . $filename . '"?page=' . $page + 1 . '">next</a>';
echo '<a href =' . $filename . '"?page=' . $num_of_pages . '">last</a>';
?>

