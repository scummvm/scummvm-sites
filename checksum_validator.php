<?php
require('db_functions.php');

$conn = db_connect();

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
  $fileset = $conn->query("SELECT file.id, name, size FROM file
  JOIN fileset ON fileset.id = file.fileset
  WHERE fileset.game = {$game['id']} AND fileset.status = 'fullmatch'");

  if ($fileset->num_rows == 0)
    continue;

  // Convert checktype, checksize to checkcode
  $fileset = $fileset->fetch_all(MYSQLI_ASSOC);
  foreach (array_values($fileset) as $index => $file) {
    $spec_checksum_res = $conn->query("SELECT checksum, checksize, checktype
    FROM filechecksum WHERE file = {$file['id']}");

    while ($spec_checksum = $spec_checksum_res->fetch_assoc()) {
      $fileset[$index][$spec_checksum['checktype'] . '-' . $spec_checksum['checksize']] = $spec_checksum['checksum'];
    }
  }

  $file_object = $json_object->files;

  // Sort the filesets by filename
  usort($file_object, function ($a, $b) {
    return strcmp($a->name, $b->name) == -1 ? -1 : 1;
  });
  usort($fileset, function ($a, $b) {
    return strcmp($a['name'], $b['name']) == -1 ? -1 : 1;
  });

  for ($i = 0, $j = 0; $i < count($fileset), $j < count($file_object); $i++, $j++) {
    $status = 'ok';
    $db_file = $fileset[$i];
    $user_file = $file_object[$j];
    $filename = $user_file->name;

    if ($db_file['name'] != $user_file->name) {
      if ($db_file['name'] > $user_file->name) {
        $status = 'unknown_file';
        $i--; // Retain same db_file for next iteration
      }
      else {
        $status = 'missing';
        $filename = $db_file['name'];
        $j--; // Retain same user_file for next iteration
      }
    }
    elseif ($db_file['size'] != $user_file->size && $status == 'ok') {
      $status = 'size_mismatch';
    }

    if ($status == 'ok') {
      foreach ($user_file->checksums as $checksum_data) {
        foreach ($checksum_data as $key => $value) {
          $user_checksum = $checksum_data->checksum;
          $user_checkcode = $checksum_data->type;
          if (strpos($user_checkcode, '-') === false)
            $user_checkcode .= '-0';

          if (strcasecmp($db_file[$user_checkcode], $user_checksum) != 0)
            $status = 'checksum_mismatch';
        }
      }
    }

    if ($status != 'ok')
      $json_response['error'] = 1;

    array_push($json_response['files'], array('status' => $status, 'name' => $filename));
  }
}

$json_response = json_encode($json_response);

function user_calc_key($user_fileset) {
  $key_string = "";
  foreach ($user_fileset as $file) {
    foreach ($file as $key => $value) {
      if ($key != 'checksums') {
        $key_string .= ':' . $value;
        continue;
      }

      foreach ($value as $checksum_pair)
        $key_string .= ':' . $checksum_pair->checksum;
    }
  }
  $key_string = trim($key_string, ':');

  return md5($key_string);
}

function file_json_to_array($file_json_object) {
  $res = array();

  foreach ($file_json_object as $key => $value) {
    if ($key != 'checksums') {
      $res[$key] = $value;
      continue;
    }

    foreach ($value as $checksum_pair)
      $res[$checksum_pair->type] = $checksum_pair->checksum;
  }

  return $res;
}

function user_insert_fileset($user_fileset, $conn) {
  $src = 'user';
  $detection = 'false';
  $key = '';
  $megakey = user_calc_key($user_fileset);
  $conn = db_connect();

  if (insert_fileset($src, $detection, $key, $megakey, $conn)) {
    foreach ($user_fileset as $file) {
      $file = file_json_to_array($file);

      insert_file($file, $detection, $src, $conn);
      foreach ($file as $key => $value) {
        if ($key != "name" && $key != "size")
          insert_filechecksum($file, $key, $conn);
      }
    }
  }
}

$conn->close();
?>

