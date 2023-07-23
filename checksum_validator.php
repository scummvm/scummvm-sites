<?php

function calc_key($json_object) {
  $key_string = '';

  $file_object = $json_object->files;
  foreach ($file_object as $file) {
    foreach ($file as $key => $value) {
      if ($key != 'checksums') {
        $key_string .= ':' . $value;
        continue;
      }

      foreach ($value as $checksum_data) {
        foreach ($checksum_data as $key => $value) {
          $key_string .= ':' . $value;
        }
      }
    }
  }

  $key_string = trim($key_string, ':');
  return md5($key_string);
}

$mysql_cred = json_decode(file_get_contents('mysql_config.json'), true);
$servername = $mysql_cred["servername"];
$username = $mysql_cred["username"];
$password = $mysql_cred["password"];
$dbname = $mysql_cred["dbname"];

// Create connection
$conn = new mysqli($servername, $username, $password);

// Check connection
if ($conn->connect_errno) {
  die("Connect failed: " . $conn->connect_error);
}

$conn->query("USE " . $dbname);

$json_string = file_get_contents('sample_json_request.json');
$json_object = json_decode($json_string);

$game_metadata = array();
foreach ($json_object as $key => $value) {
  if ($key == 'files')
    continue;

  $game_metadata[$key] = $value;
}

// Find game(s) that fit the metadata
// $query = "SELECT game.id FROM game
// JOIN engine ON game.engine = engine.id
// WHERE gameid = '{$game_metadata['gameid']}'
// AND engineid = '{$game_metadata['engineid']}'
// AND extra = '{$game_metadata['extra']}'
// AND platform = '{$game_metadata['platform']}'
// AND language = '{$game_metadata['language']}'";
// $games = $conn->query($query)->fetch_all();

$matches = $conn->query(sprintf("SELECT game.id FROM fileset
JOIN game ON fileset.game = game.id
WHERE `key` = '%s' AND fileset.status = 'fullmatch'", calc_key($json_object)));

if ($matches->num_rows == 0)
  echo "No games found / Files corrupted";
else
  echo "Game files are correct";

$conn->close();
?>

