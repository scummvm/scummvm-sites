<?php
require "pagination.php";

$filename = "games_list.php";
$count_query = "SELECT COUNT(id) FROM game";
$select_query = "SELECT engineid, gameid, extra, platform, language, game.name as 'game name', status
FROM game
JOIN engine ON engine.id = game.engine
JOIN fileset ON game.id = fileset.game";

$filters = array(
  "engineid" => "engine",
  "gameid" => "game",
  "extra" => "game",
  "platform" => "game",
  "language" => "game",
  "name" => "game",
  "status" => "fileset"
);

create_page($filename, 25, $count_query, $select_query, $filters);
?>

