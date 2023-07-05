<?php
require "pagination.php";

$filename = "logs.php";
$records_table = "log";
$select_query = "SELECT `timestamp`, category, user, `text`
FROM log";

$filters = array(
  "category" => "log",
  "user" => "log"
);

create_page($filename, 25, $records_table, $select_query, $filters);
?>

