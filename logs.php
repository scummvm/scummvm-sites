<?php
require "pagination.php";

$filename = "logs.php";
$count_query = "SELECT COUNT(id) FROM log";
$select_query = "SELECT `timestamp`, category, user, `text`
FROM log";

create_page($filename, 25, $count_query, $select_query);
?>

