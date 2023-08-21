<?php
require __DIR__ . '/include/pagination.php';

$filename = "user_games_list.php";
$records_table = "game";
$select_query = "SELECT engineid, gameid, extra, platform, language, game.name,
status, fileset.id as fileset
FROM fileset
LEFT JOIN game ON game.id = fileset.game
LEFT JOIN engine ON engine.id = game.engine
WHERE status = 'user'";
$order = "ORDER BY gameid";

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

$mapping = array(
  'engine.id' => 'game.engine',
  'game.id' => 'fileset.game',
);

create_page($filename, 200, $records_table, $select_query, $order, $filters, $mapping);
?>

