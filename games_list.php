<?php
require "pagination.php";

$filename = "games_list.php";
$records_table = "game";
$select_query = "SELECT engineid, gameid, extra, platform, language, game.name as 'game name', status
FROM game
JOIN engine ON engine.id = game.engine
JOIN fileset ON game.id = fileset.game";

// Filter column => table
$filters = array(
  "engineid" => "engine",
  "gameid" => "game",
  "extra" => "game",
  "platform" => "game",
  "language" => "game",
  "name" => "game",
  "status" => "fileset"
);

create_page($filename, 25, $records_table, $select_query, $filters);
?>

