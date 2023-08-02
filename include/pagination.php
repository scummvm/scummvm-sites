<?php
$stylesheet = 'style.css';
$jquery_file = 'https://code.jquery.com/jquery-3.7.0.min.js';
$js_file = 'js_functions.js';
echo "<link rel='stylesheet' href='{$stylesheet}'>\n";
echo "<script type='text/javascript' src='{$jquery_file}'></script>\n";
echo "<script type='text/javascript' src='{$js_file}'></script>\n";

/**
 * Return a string denoting which two columns link two tables
 */
function get_join_columns($table1, $table2, $mapping) {
  foreach ($mapping as $primary => $foreign) {
    $primary = explode('.', $primary);
    $foreign = explode('.', $foreign);
    if (($primary[0] == $table1 && $foreign[0] == $table2) ||
      ($primary[0] == $table2 && $foreign[0] == $table1))
      return "{$primary[0]}.{$primary[1]} = {$foreign[0]}.{$foreign[1]}";
  }

  echo "No primary-foreign key mapping provided. Filter is invalid";
}

function create_page($filename, $results_per_page, $records_table, $select_query, $order, $filters = array(), $mapping = array()) {
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

  // If there exist get variables that are for filtering
  $_GET = array_filter($_GET);
  if (isset($_GET['sort'])) {
    $column = $_GET['sort'];
    $column = explode('-', $column);
    $order = "ORDER BY {$column[0]}";

    if (strpos($_GET['sort'], 'desc') !== false)
      $order .= " DESC";
  }

  if (array_diff(array_keys($_GET), array('page', 'sort'))) {
    $condition = "WHERE ";
    $tables = array();
    foreach ($_GET as $key => $value) {
      if ($key == 'page' || $key == 'sort' || $value == '')
        continue;

      array_push($tables, $filters[$key]);
      $condition .= $condition != "WHERE " ? " AND {$filters[$key]}.{$key} REGEXP '{$value}'" : "{$filters[$key]}.{$key} REGEXP '{$value}'";
    }
    if ($condition == "WHERE ")
      $condition = "";

    // If more than one table is to be searched
    $from_query = $records_table;
    if (count($tables) > 1 || $tables[0] != $records_table)
      for ($i = 0; $i < count($tables); $i++) {
        if ($tables[$i] == $records_table)
          continue;

        $from_query .= sprintf(" JOIN %s ON %s", $tables[$i], get_join_columns($records_table, $tables[$i], $mapping));
      }

    $num_of_results = $conn->query(
      "SELECT COUNT({$records_table}.id) FROM {$from_query} {$condition}")->fetch_array()[0];
  }
  // If $records_table has a JOIN (multiple tables)
  elseif (preg_match("/JOIN/", $records_table) !== false) {
    $first_table = explode(" ", $records_table)[0];
    $num_of_results = $conn->query("SELECT COUNT({$first_table}.id) FROM {$records_table}")->fetch_array()[0];
  }
  else {
    $num_of_results = $conn->query("SELECT COUNT(id) FROM {$records_table}")->fetch_array()[0];
  }
  $num_of_pages = ceil($num_of_results / $results_per_page);
  if ($num_of_results == 0) {
    echo "No results for given filters";
    return;
  }

  if (!isset($_GET['page'])) {
    $page = 1;
  }
  else {
    $page = max(1, min($_GET['page'], $num_of_pages));
  }

  $offset = ($page - 1) * $results_per_page;

  // If there exist get variables that are for filtering
  if (array_diff(array_keys($_GET), array('page'))) {
    $condition = "WHERE ";
    foreach ($_GET as $key => $value) {
      $value = mysqli_real_escape_string($conn, $value);
      if (!isset($filters[$key]))
        continue;

      $condition .= $condition != "WHERE " ? "AND {$filters[$key]}.{$key} REGEXP '{$value}'" : "{$filters[$key]}.{$key} REGEXP '{$value}'";
    }
    if ($condition == "WHERE ")
      $condition = "";

    $query = "{$select_query} {$condition} {$order} LIMIT {$results_per_page} OFFSET {$offset}";
  }
  else {
    $query = "{$select_query} {$order} LIMIT {$results_per_page} OFFSET {$offset}";
  }
  $result = $conn->query($query);


  // Table
  echo "<form id='filters-form' method='GET' onsubmit='remove_empty_inputs()'>";
  echo "<table>\n";

  $counter = $offset + 1;
  while ($row = $result->fetch_assoc()) {
    if ($counter == $offset + 1) { // If it is the first run of the loop
      if (count($filters) > 0) {
        echo "<tr class=filter><td></td>";
        foreach (array_keys($row) as $key) {
          if (!isset($filters[$key])) {
            echo "<td class=filter />";
            continue;
          }

          // Filter textbox
          $filter_value = isset($_GET[$key]) ? $_GET[$key] : "";

          echo "<td class=filter><input type=text class=filter placeholder='{$key}' name='{$key}' value='{$filter_value}'/></td>\n";
        }
        echo "</tr>";
        echo "<tr class=filter><td></td><td class=filter><input type=submit value='Submit'></td></tr>";
      }

      echo "<th/>\n"; // Numbering column
      foreach (array_keys($row) as $key) {
        if ($key == 'fileset')
          continue;

        // Preserve GET variables
        $vars = "";
        foreach ($_GET as $k => $v) {
          if ($k == 'sort' && $v == $key)
            $vars .= "&{$k}={$v}-desc";
          elseif ($k != 'sort')
            $vars .= "&{$k}={$v}";
        }

        if (strpos($vars, "&sort={$key}") === false)
          echo "<th><a href='{$filename}?{$vars}&sort={$key}'>{$key}</th>\n";
        else
          echo "<th><a href='{$filename}?{$vars}'>{$key}</th>\n";
      }
    }

    if ($filename == 'games_list.php')
      echo "<tr class=games_list onclick='hyperlink(\"fileset.php?id={$row['fileset']}\")'>\n";
    else
      echo "<tr>\n";
    echo "<td>{$counter}.</td>\n";
    foreach ($row as $key => $value) {
      if ($key == 'fileset')
        continue;

      // Add links to fileset in logs table
      $matches = array();
      if (preg_match("/Fileset:(\d+)/", $value, $matches, PREG_OFFSET_CAPTURE)) {
        $value = substr($value, 0, $matches[0][1]) .
          "<a href='fileset.php?id={$matches[1][0]}'>{$matches[0][0]}</a>" .
          substr($value, $matches[0][1] + strlen($matches[0][0]));
      }

      echo "<td>{$value}</td>\n";
    }
    echo "</tr>\n";

    $counter++;
  }

  echo "</table>\n";
  echo "</form>\n";

  // Preserve GET variables
  $vars = "";
  foreach ($_GET as $key => $value) {
    if ($key == 'page')
      continue;
    $vars .= "&{$key}={$value}";
  }

  // Navigation elements
  if ($num_of_pages > 1) {
    echo "<form method='GET'>\n";

    // Preserve GET variables on form submit
    foreach ($_GET as $key => $value) {
      if ($key == 'page')
        continue;

      $key = htmlspecialchars($key);
      $value = htmlspecialchars($value);
      if ($value != "")
        echo "<input type='hidden' name='{$key}' value='{$value}'>";
    }

    echo "<div class=pagination>\n";
    if ($page > 1) {
      echo "<a href={$filename}?{$vars}>❮❮</a>\n";
      echo sprintf("<a href=%s?page=%d%s>❮</a>\n", $filename, $page - 1, $vars);
    }
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
    if ($page < $num_of_pages) {
      echo sprintf("<a href=%s?page=%d%s>❯</a>\n", $filename, $page + 1, $vars);
      echo "<a href={$filename}?page={$num_of_pages}{$vars}>❯❯</a>\n";
    }

    echo "<input type='text' name='page' placeholder='Page No'>\n";
    echo "<input type='submit' value='Submit'>\n";
    echo "</div>\n";

    echo "</form>\n";
  }

}
?>

