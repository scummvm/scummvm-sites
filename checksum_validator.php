<?php
require('dat_parser.php');

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
$query = "SELECT game.id FROM game
JOIN engine ON game.engine = engine.id
WHERE gameid = '{$game_metadata['gameid']}'
AND engineid = '{$game_metadata['engineid']}'
AND extra = '{$game_metadata['extra']}'
AND platform = '{$game_metadata['platform']}'
AND language = '{$game_metadata['language']}'";
$games = $conn->query($query);

$json_response = array(
  'error' => 0,
  'files' => array()
);

// Check if all files in fullmatch filesets are present with user
while ($game = $games->fetch_array()) {
  $fileset = $conn->query("SELECT name, size,
  checksize, checktype, filechecksum.checksum
  FROM filechecksum
  JOIN file ON file.id = filechecksum.file
  JOIN fileset ON fileset.id = file.fileset
  WHERE fileset.game = {$game['id']} AND fileset.status = 'fullmatch'");

  if ($fileset->num_rows == 0)
    continue;

  $file_object = $json_object->files;
  print_r($fileset);

  $mismatch = false;
  foreach ($file_object as $user_file) {
    $status = 'ok';
    $db_file = $fileset->fetch_array();

    if (!($db_file['name'] == $user_file['name'])) {
      $mismatch = true;
      $status = 'unknown';
    }


    if ($mismatch)
      break;

    foreach ($value as $checksum_data) {
      if ($mismatch)
        break;

      foreach ($checksum_data as $key => $value) {
        $user_checkcode = $checksum_data->type;
        $user_checksum = $checksum_data->checksum;

        list($checksize, $checktype, $checksum) = get_checksum_props($user_checkcode, $user_checksum);
        $mismatch == !($db_file['checksum'] == $checksum) ||
          !($db_file['checktype'] == $checktype) ||
          !($db_file['checksize'] == $checksize);

        if ($mismatch)
          break;
      }
    }
  }


}

$conn->close();
?>

