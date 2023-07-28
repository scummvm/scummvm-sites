<?php
require "pagination.php";

$filename = "logs.php";
$records_table = "log";
$select_query = "SELECT id, `timestamp`, category, user, `text`
FROM log";
$order = "ORDER BY `timestamp` DESC, id DESC";

$filters = array(
  'id' => 'log',
  'timestamp' => 'log',
  'category' => 'log',
  'user' => 'log',
  'text' => 'log'
);

create_page($filename, 25, $records_table, $select_query, $order, "logs.php", $filters);
?>

