<?php
require __DIR__ . '/../include/db_functions.php';

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

function user_insert_queue($user_fileset, $conn) {
  $query = sprintf("INSERT INTO queue (time, notes, fileset, ticketid, userid, commit)
  VALUES (%d, NULL, @fileset_last, NULL, NULL, NULL)", time());

  $conn->query($query);
}

function user_insert_fileset($user_fileset, $ip, $conn) {
  $src = 'user';
  $detection = false;
  $key = '';
  $megakey = user_calc_key($user_fileset);
  $transaction_id = $conn->query("SELECT MAX(`transaction`) FROM transactions")->fetch_array()[0] + 1;
  $log_text = "from user submitted files";
  $conn = db_connect();

  // Set timestamp of fileset insertion
  $conn->query(sprintf("SET @fileset_time_last = %d", time()));

  if (insert_fileset($src, $detection, $key, $megakey, $transaction_id, $log_text, $conn, $ip)) {
    foreach ($user_fileset as $file) {
      $file = file_json_to_array($file);

      insert_file($file, $detection, $src, $conn);
      foreach ($file as $key => $value) {
        if ($key != "name" && $key != "size")
          insert_filechecksum($file, $key, $conn);
      }
    }
  }

  $fileset_id = $conn->query("SELECT @fileset_last")->fetch_array()[0];
  $conn->commit();
  return $fileset_id;
}


/**
 * (Attempt to) match fileset that have fileset.game as NULL
 */
function match_user_filesets() {
  $conn = db_connect();

  // Getting unmatched filesets
  $unmatched_filesets = array();

  $unmatched_files = $conn->query("SELECT fileset.id, filechecksum.checksum, src, status
  FROM fileset
  JOIN file ON file.fileset = fileset.id
  JOIN filechecksum ON file.id = filechecksum.file
  WHERE fileset.game IS NULL AND status = 'user'");
  $unmatched_files = $unmatched_files->fetch_all();

  // Splitting them into different filesets
  for ($i = 0; $i < count($unmatched_files); $i++) {
    $cur_fileset = $unmatched_files[$i][0];
    $temp = array();
    while ($i < count($unmatched_files) - 1 && $cur_fileset == $unmatched_files[$i][0]) {
      array_push($temp, $unmatched_files[$i]);
      $i++;
    }
    array_push($unmatched_filesets, $temp);
  }

  foreach ($unmatched_filesets as $fileset) {
    $matching_games = find_matching_game($fileset);

    if (count($matching_games) != 1) // If there is no match/non-unique match
      continue;

    $matched_game = $matching_games[0];

    // Update status depending on $matched_game["src"] (dat -> partialmatch, scan -> fullmatch)
    $status = $fileset[0][2];
    if ($fileset[0][2] == "dat")
      $status = "partialmatch";
    elseif ($fileset[0][2] == "scan")
      $status = "fullmatch";

    // Convert NULL values to string with value NULL for printing
    $matched_game = array_map(function ($val) {
      return (is_null($val)) ? "NULL" : $val;
    }, $matched_game);

    $category_text = "Matched from {$fileset[0][2]}";
    $log_text = "Matched game {$matched_game['engineid']}:
    {$matched_game['gameid']}-{$matched_game['platform']}-{$matched_game['language']}
    variant {$matched_game['key']}. State {$status}. Fileset:{$fileset[0][0]}.";

    // Updating the fileset.game value to be $matched_game["id"]
    $query = sprintf("UPDATE fileset
    SET game = %d, status = '%s', `key` = '%s'
    WHERE id = %d", $matched_game["id"], $status, $matched_game["key"], $fileset[0][0]);

    if (!$conn->commit())
      echo "Matching user fileset failed\n";
  }
}

/*
 * Delete the original detection fileset and replace it with the newly matched
 * fileset
 */
function merge_user_filesets() {
    $history_last = merge_filesets($matched_game["fileset"], $fileset[0][0]);

    if ($conn->query($query)) {
      $user = 'cli:' . get_current_user();

      // Merge log
      create_log("Fileset merge", $user,
        mysqli_real_escape_string($conn, "Merged Fileset:{$matched_game['fileset']} and Fileset:{$fileset[0][0]}"));

      // Matching log
      $log_last = create_log(mysqli_real_escape_string($conn, $category_text), $user,
        mysqli_real_escape_string($conn, $log_text));

      // Add log id to the history table
    $conn->query("UPDATE history SET log = {$log_last} WHERE id = {$history_last}");
  }
}

?>

