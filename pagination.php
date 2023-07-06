<?php
$stylesheet = "style.css";
echo "<link rel='stylesheet' href='{$stylesheet}'>\n";

function create_page($filename, $results_per_page, $records_table, $select_query, $filters = array()) {
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

  if (isset($_GET['column']) && isset($_GET['value'])) {
    $column = $_GET['column'];
    $value = mysqli_real_escape_string($conn, $_GET['value']);
    $num_of_results = $conn->query(
      "SELECT COUNT(id) FROM {$filters[$column]} WHERE {$column} = '{$value}'")->fetch_array()[0];
  }
  else {
    $num_of_results = $conn->query("SELECT COUNT(id) FROM {$records_table}")->fetch_array()[0];
  }
  $num_of_pages = ceil($num_of_results / $results_per_page);

  if (!isset($_GET['page'])) {
    $page = 1;
  }
  else {
    $page = max(1, min($_GET['page'], $num_of_pages));
  }

  $offset = ($page - 1) * $results_per_page;
  if (isset($_GET['column']) && isset($_GET['value'])) {
    $query = "{$select_query} WHERE {$column} = '{$value}' LIMIT {$results_per_page} OFFSET {$offset}";
  }
  else {
    $query = "{$select_query} LIMIT {$results_per_page} OFFSET {$offset}";
  }

  $result = $conn->query($query);


  // Create filter dropdown
  if ($filters) {
    echo "<div class='filter'>\n";
    echo "<form name='filter' method='GET'>\n";
    echo "Filter: ";

    echo "<select name='column'>\n";
    foreach (array_keys($filters) as $key) {
      echo "<option>{$key}</option>\n";
    }
    echo "</select>\n";
    echo "<input type='text' name='value' placeholder='Value'>\n";

    echo "<input type='submit' name='submit' value='Select' />\n";
    echo "</form>\n";
    echo "</div>\n";
  }


  // Table
  echo "<table>\n";
  echo "<th/>\n"; // Numbering column

  $counter = $offset + 1;
  while ($row = $result->fetch_assoc()) {
    if ($counter == $offset + 1) { // If it is the first run of the loop
      foreach (array_keys($row) as $key) {
        echo "<th>{$key}</th>\n";
      }
    }

    echo "<tr>\n";
    echo "<td>{$counter}.</td>\n";
    foreach (array_values($row) as $value) {
      // Add hyperlink to filesets
      $matches = array();
      if (preg_match("/Fileset:(\d+)/", $value, $matches, PREG_OFFSET_CAPTURE)) {
        $value = substr($value, 0, $matches[0][1]) . "<a href='fileset.php?id={$matches[1][0]}'>{$matches[0][0]}</a>";
      }

      echo "<td>{$value}</td>\n";
    }
    echo "</tr>\n";

    $counter++;
  }

  echo "</table>\n";

  // Preserve GET variables
  $vars = "";
  foreach ($_GET as $key => $value) {
    if ($key == 'page')
      continue;
    $vars .= "&{$key}={$value}";
  }

  // Navigation elements
  echo "<form method='GET'>\n";
  echo "<div class=pagination>\n";
  if ($page > 1)
    echo "<a href={$filename}?{$vars}>❮❮</a>\n";
  if ($page - 2 > 1)
    echo "<div class=more>...</div>\n";


  for ($i = $page - 2; $i <= $page + 2; $i++) {
    if ($i >= 1 && $i <= $num_of_pages) {

      if ($i == $page)
        echo sprintf("<a class=active href=%s?page=%d%s>%d</a>\n", $filename, $i, $vars, $i);
      else
        echo sprintf("<a href=%s?page=%d%s>%d</a>\n", $filename, $i, $vars, $i);
    }
  }

  if ($page + 2 < $num_of_pages)
    echo "<div class=more>...</div>\n";
  if ($page < $num_of_pages)
    echo "<a href={$filename}?page={$num_of_pages}{$vars}>❯❯</a>\n";

  echo "<input type='text' name='page' placeholder='Page Number'>\n";
  echo "<input type='submit' name='submit' value='Submit'>\n";
  echo "</form>\n";

  echo "</div>\n";

}
?>

