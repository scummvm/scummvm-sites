<?php

/**
 * Create and return a mysqli connection
 */
function db_connect() {
  $mysql_cred = json_decode(file_get_contents('mysql_config.json'), true);
  $servername = $mysql_cred["servername"];
  $username = $mysql_cred["username"];
  $password = $mysql_cred["password"];
  $dbname = $mysql_cred["dbname"];

  // Create connection
  mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
  $conn = new mysqli($servername, $username, $password);
  $conn->set_charset('utf8mb4');
  $conn->autocommit(FALSE);

  // Check connection
  if ($conn->connect_errno) {
    die("Connect failed: " . $conn->connect_error);
  }

  $conn->query("USE " . $dbname);

  return $conn;
}

/**
 * Retrieves the checksum and checktype of a given type + checksum
 * eg: md5-5000 t:12345... -> 5000, md5-t, 12345...
 */
function get_checksum_props($checkcode, $checksum) {
  $checksize = 0;
  $checktype = $checkcode;
  if (strpos($checkcode, '-') !== false) {
    $temp = explode('-', $checkcode)[1];
    if ($temp == '1M' || is_numeric($temp))
      $checksize = $temp;
    $checktype = explode('-', $checkcode)[0];
  }

  if (strpos($checksum, ':') !== false) {
    $prefix = explode(':', $checksum)[0];

    if (strpos($prefix, 't') !== false)
      $checktype .= "-" . 't';
    $checksum = explode(':', $checksum)[1];
  }

  return array($checksize, $checktype, $checksum);
}

/**
 * Routine for inserting a game into the database - inserting into engine and
 * game tables
 */
function insert_game($engine_name, $engineid, $title, $gameid, $extra, $platform, $lang, $conn) {
  // Set @engine_last if engine already present in table
  $exists = false;
  if ($res = $conn->query(sprintf("SELECT id FROM engine WHERE engineid = '%s'", $engineid))) {
    if ($res->num_rows > 0) {
      $exists = true;
      $conn->query(sprintf("SET @engine_last = '%d'", $res->fetch_array()[0]));
    }
  }

  // Insert into table if not present
  if (!$exists) {
    $query = sprintf("INSERT INTO engine (name, engineid)
  VALUES ('%s', '%s')", mysqli_real_escape_string($conn, $engine_name), $engineid);
    $conn->query($query);
    $conn->query("SET @engine_last = LAST_INSERT_ID()");
  }

  // Insert into game
  $query = sprintf("INSERT INTO game (name, engine, gameid, extra, platform, language)
  VALUES ('%s', @engine_last, '%s', '%s', '%s', '%s')", mysqli_real_escape_string($conn, $title),
    $gameid, mysqli_real_escape_string($conn, $extra), $platform, $lang);
  $conn->query($query);
  $conn->query("SET @game_last = LAST_INSERT_ID()");
}

function insert_fileset($src, $detection, $key, $megakey, $conn) {
  $status = $detection ? "detection" : $src;
  $game = "NULL";
  $key = $key == "" ? "NULL" : "'{$key}'";
  $megakey = $megakey == "" ? "NULL" : "'{$megakey}'";

  if ($detection) {
    $status = "detection";
    $game = "@game_last";
  }

  // Check if key/megakey already exists, if so, skip insertion (no quotes on purpose)
  if ($detection)
    $existing_entry = $conn->query("SELECT id FROM fileset WHERE `key` = {$key}");
  else
    $existing_entry = $conn->query("SELECT id FROM fileset WHERE megakey = {$megakey}");

  if ($existing_entry->num_rows > 0) {
    if (!$detection)
      return false;

    $existing_entry = $existing_entry->fetch_array()[0];
    $conn->query("UPDATE fileset SET `timestamp` = FROM_UNIXTIME(@fileset_time_last)
                      WHERE id = {$existing_entry}");
    $conn->query("UPDATE fileset SET status = 'detection'
                    WHERE id = {$existing_entry} AND status = 'obsolete'");
    $conn->query("DELETE FROM game WHERE id = @game_last");
    return false;
  }

  // $game and $key should not be parsed as a mysql string, hence no quotes
  $query = "INSERT INTO fileset (game, status, src, `key`, megakey, `timestamp`)
  VALUES ({$game}, '{$status}', '{$src}', {$key}, {$megakey}, FROM_UNIXTIME(@fileset_time_last))";
  $conn->query($query);
  $conn->query("SET @fileset_last = LAST_INSERT_ID()");

  return true;
}

/**
 * Routine for inserting a file into the database, inserting into all
 * required tables
 * $file is an associated array (the contents of 'rom')
 * If checksum of the given checktype doesn't exists, silently fails
 */
function insert_file($file, $detection, $src, $conn) {
  // Find md5-5000, or else use first checksum value
  $checksum = "";
  $checksize = 5000;
  if (isset($file["md5-5000"])) {
    $checksum = $file["md5-5000"];
  }
  else {
    foreach ($file as $key => $value) {
      if (strpos($key, "md5") !== false) {
        list($checksize, $checktype, $checksum) = get_checksum_props($key, $value);
        break;
      }
    }
  }

  $query = sprintf("INSERT INTO file (name, size, checksum, fileset, detection)
  VALUES ('%s', '%s', '%s', @fileset_last, %d)", mysqli_real_escape_string($conn, $file["name"]),
    $file["size"], $checksum, $detection);
  $conn->query($query);

  if ($detection)
    $conn->query("UPDATE fileset SET detection_size = {$checksize} WHERE id = @fileset_last AND detection_size IS NULL");
  $conn->query("SET @file_last = LAST_INSERT_ID()");
}

function insert_filechecksum($file, $checktype, $conn) {
  if (!array_key_exists($checktype, $file))
    return;

  $checksum = $file[$checktype];
  list($checksize, $checktype, $checksum) = get_checksum_props($checktype, $checksum);

  $query = sprintf("INSERT INTO filechecksum (file, checksize, checktype, checksum)
  VALUES (@file_last, '%s', '%s', '%s')", $checksize, $checktype, $checksum);
  $conn->query($query);
}

/**
 * Create an entry to the log table on each call of db_insert() or
 * populate_matching_games()
 */
function create_log($category, $user, $text) {
  $conn = db_connect();
  $conn->query(sprintf("INSERT INTO log (`timestamp`, category, user, `text`)
  VALUES (FROM_UNIXTIME(%d), '%s', '%s', '%s')", time(), $category, $user, $text));
  $log_last = $conn->query("SELECT LAST_INSERT_ID()")->fetch_array()[0];

  if (!$conn->commit())
    echo "Creating log failed\n";

  return $log_last;
}

/**
 * Calculate `key` value as md5("file1:size:md5:file2:...")
 */
function calc_key($files) {
  $key_string = "";
  foreach ($files as $file) {
    foreach ($file as $key => $value) {
      $key_string .= ':' . $value;
    }
  }
  $key_string = trim($key_string, ':');
  return md5($key_string);
}

/**
 * Insert values from the associated array into the DB
 * They will be inserted under gameid NULL as the game itself is unconfirmed
 */
function db_insert($data_arr) {
  $header = $data_arr[0];
  $game_data = $data_arr[1];
  $resources = $data_arr[2];
  $filepath = $data_arr[3];

  $conn = db_connect();

  /**
   * Author can be:
   *  scummvm -> Detection Entries
   *  scanner -> CLI scanner tool in python
   *  _anything else_ -> DAT file
   */
  $author = $header["author"];
  $version = $header["version"];

  /**
   * status can be:
   *  detection -> Detection entries (source of truth)
   *  user -> Submitted by users via ScummVM, unmatched (Not used in the parser)
   *  scan -> Submitted by cli/scanner, unmatched
   *  dat -> Submitted by DAT, unmatched
   *  partialmatch -> Submitted by DAT, matched
   *  fullmatch -> Submitted by cli/scanner, matched
   *  obsolete -> Detection entries that are no longer part of the detection set
   */
  $src = "";
  if ($author == "scan" || $author == "scummvm")
    $src = $author;
  else
    $src = "dat";

  $detection = ($src == "scummvm");
  $status = $detection ? "detection" : $src;

  // Set timestamp of fileset insertion
  $conn->query(sprintf("SET @fileset_time_last = %d", time()));

  foreach ($game_data as $fileset) {
    if ($detection) {
      $engine_name = $fileset["engine"];
      $engineid = $fileset["sourcefile"];
      $gameid = $fileset["name"];
      $title = $fileset["title"];
      $extra = $fileset["extra"];
      $platform = $fileset["platform"];
      $lang = $fileset["language"];

      insert_game($engine_name, $engineid, $title, $gameid, $extra, $platform, $lang, $conn);
    }
    elseif ($src == "dat")
      if (isset($fileset['romof']) && isset($resources[$fileset['romof']]))
        $fileset["rom"] = array_merge($fileset["rom"], $resources[$fileset["romof"]]["rom"]);

    $key = $detection ? calc_key($fileset['rom']) : "";
    $megakey = !$detection ? calc_key($fileset['rom']) : "";
    if (insert_fileset($src, $detection, $key, $megakey, $conn)) {
      foreach ($fileset["rom"] as $file) {
        insert_file($file, $detection, $src, $conn);
        foreach ($file as $key => $value) {
          if ($key != "name" && $key != "size")
            insert_filechecksum($file, $key, $conn);
        }
      }
    }
  }

  if ($detection)
    $conn->query("UPDATE fileset SET status = 'obsolete'
                  WHERE `timestamp` != FROM_UNIXTIME(@fileset_time_last)
                  AND status = 'detection'");

  $category_text = "Uploaded from {$src}";
  $log_text = sprintf("Loaded DAT file, filename '%s', size %d, author '%s', version %s.
  State '%s'. Fileset:%d.",
    $filepath, filesize($filepath), $author, $version, $status,
    $conn->query("SELECT @fileset_last")->fetch_array()[0]);

  if (!$conn->commit())
    echo "Inserting failed\n";
  else {
    $user = 'cli:' . get_current_user();
    create_log(mysqli_real_escape_string($conn, $category_text), $user, mysqli_real_escape_string($conn, $log_text));
  }
}

/**
 * Compare 2 dat filesets to find if they are equivalent or not
 */
function compare_filesets($id1, $id2, $conn) {
  $fileset1 = $conn->query("SELECT name, size, checksum
                            FROM file WHERE fileset = '{$id1}'")->fetch_all();
  $fileset2 = $conn->query("SELECT name, size, checksum
                            FROM file WHERE fileset = '{$id2}'")->fetch_all();

  // Sort filesets on checksum
  usort($fileset1, function ($a, $b) {
    return $a[2] <=> $b[2];
  });
  usort($fileset2, function ($a, $b) {
    return $a[2] <=> $b[2];
  });

  if (count($fileset1) != count($fileset2))
    return false;

  for ($i = 0; $i < count($fileset1); $i++) {
    // If checksums do not match
    if ($fileset1[2] != $fileset2[2])
      return false;
  }

  return True;
}

/**
 * Return fileset statuses that can be merged with set of given status
 * eg: scan and dat -> detection
 *     fullmatch -> partialmatch, detection
 */
function status_to_match($status) {
  $order = array("detection", "dat", "scan", "partialmatch", "fullmatch");
  return array_slice($order, 0, array_search($status, $order));
}

/**
 * Detects games based on the file descriptions in $dat_arr
 * Compares the files with those in the detection entries table
 * $game_files consists of both the game ( ) and resources ( ) parts
 */
function find_matching_game($game_files) {
  $matching_games = array(); // All matching games
  $matching_filesets = array(); // All filesets containing one file from $game_files
  $matches_count = 0; // Number of files with a matching detection entry

  $conn = db_connect();

  foreach ($game_files as $file) {
    $checksum = $file[1];

    $query = "SELECT file.fileset as file_fileset
    FROM filechecksum
    JOIN file ON filechecksum.file = file.id
    WHERE filechecksum.checksum = '{$checksum}' AND file.detection = TRUE";
    $records = $conn->query($query)->fetch_all();

    // If file is not part of detection entries, skip it
    if (count($records) == 0)
      continue;

    $matches_count++;
    foreach ($records as $record)
      array_push($matching_filesets, $record[0]);
  } // Check if there is a fileset_id that is present in all results
  foreach (array_count_values($matching_filesets) as $key => $value) {
    $count_files_in_fileset = $conn->query(sprintf("SELECT COUNT(file.id) FROM file
    JOIN fileset ON file.fileset = fileset.id
    WHERE fileset.id = '%s'", $key))->fetch_array()[0];

    // We use < instead of != since one file may have more than one entry in the fileset
    // We see this in Drascula English version, where one entry is duplicated
    if ($value < $matches_count || $value < $count_files_in_fileset)
      continue;

    $records = $conn->query(sprintf("SELECT engineid, game.id, gameid, platform,
    language, `key`, src, fileset.id as fileset
    FROM game
    JOIN fileset ON fileset.game = game.id
    JOIN engine ON engine.id = game.engine
    WHERE fileset.id = '%s'", $key));

    array_push($matching_games, $records->fetch_array());
  }

  if (count($matching_games) != 1)
    return $matching_games;

  // Check the current fileset priority with that of the match
  $records = $conn->query(sprintf("SELECT id FROM fileset, ({$query}) AS res
      WHERE id = file_fileset AND
      status IN ('%s')", implode("', '", status_to_match($game_files[3]))));

  // If priority order is correct
  if ($records->num_rows != 0)
    return $matching_games;

  if (compare_filesets($matching_games[0]['fileset'], $game_files[0][0], $conn)) {
    $conn->query("UPDATE fileset SET `delete` = TRUE WHERE id = {$game_files[0]}");
    return array();
  }

  return $matching_games;
}

/**
 * Merge two filesets without duplicating files
 * Used after matching an unconfirmed fileset with a detection entry
 */
function merge_filesets($detection_id, $dat_id) {
  $conn = db_connect();

  $detection_files = $conn->query(sprintf("SELECT DISTINCT(filechecksum.checksum), checksize, checktype
  FROM filechecksum JOIN file on file.id = filechecksum.file
  WHERE fileset = '%d'", $detection_id))->fetch_all();

  foreach ($detection_files as $file) {
    $checksum = $file[0];
    $checksize = $file[1];
    $checktype = $file[2];

    // Delete original detection entry so newly matched fileset is the only fileset for game
    $conn->query(sprintf("DELETE FROM file
    WHERE checksum = '%s' AND fileset = %d LIMIT 1", $checksum, $detection_id));

    // Mark files present in the detection entries
    $conn->query(sprintf("UPDATE file
    JOIN filechecksum ON filechecksum.file = file.id
    SET detection = TRUE,
    checksize = %d,
    checktype = '%s'
    WHERE fileset = '%d' AND filechecksum.checksum = '%s'",
      $checksize, $checktype, $dat_id, $checksum));
  }

  // Add fileset pair to history ($dat_id is the new fileset for $detection_id)
  $conn->query(sprintf("INSERT INTO history (`timestamp`, fileset, oldfileset)
  VALUES (FROM_UNIXTIME(%d), %d, %d)", time(), $dat_id, $detection_id));
  $history_last = $conn->query("SELECT LAST_INSERT_ID()")->fetch_array()[0];

  $conn->query("UPDATE history SET fileset = {$dat_id} WHERE fileset = {$detection_id}");

  // Delete original fileset
  $conn->query("DELETE FROM fileset WHERE id = {$detection_id}");

  if (!$conn->commit())
    echo "Error merging filesets\n";

  return $history_last;
}

/**
 * (Attempt to) match fileset that have fileset.game as NULL
 * This will delete the original detection fileset and replace it with the newly
 * matched fileset
 */
function populate_matching_games() {
  $conn = db_connect();

  // Getting unmatched filesets
  $unmatched_filesets = array();

  $unmatched_files = $conn->query("SELECT fileset.id, filechecksum.checksum, src, status
  FROM fileset
  JOIN file ON file.fileset = fileset.id
  JOIN filechecksum ON file.id = filechecksum.file
  WHERE fileset.game IS NULL");
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

    $history_last = merge_filesets($matched_game["fileset"], $fileset[0][0]);

    if ($conn->query($query)) {
      $user = 'cli:' . get_current_user();
      $log_last = create_log(mysqli_real_escape_string($conn, $category_text), $user,
        mysqli_real_escape_string($conn, $log_text));

      // Add log id to the history table
      $conn->query("UPDATE history SET log = {$log_last} WHERE id = {$history_last}");
    }

    if (!$conn->commit())
      echo "Updating matched games failed\n";
  }
}


?>

