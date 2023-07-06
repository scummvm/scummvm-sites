<?php

ini_set('memory_limit', '512M');

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

function remove_quotes($string) {
  // Remove quotes from value if they are present
  if ($string[0] == "\"")
    $string = substr($string, 1, -1);

  return $string;
}

/**
 * Convert string of checksum data from rom into associated array
 * Returns array instead of updating one like map_key_values
 */
function map_checksum_data($content_string) {
  $arr = array();
  $temp = preg_split('/("[^"]*")|\h+/', $content_string, -1, PREG_SPLIT_NO_EMPTY | PREG_SPLIT_DELIM_CAPTURE);

  for ($i = 1; $i < count($temp); $i += 2) {
    if ($temp[$i] == ')')
      continue;
    $temp[$i + 1] = remove_quotes($temp[$i + 1]);

    $arr[$temp[$i]] = stripslashes($temp[$i + 1]);
  }

  return $arr;
}

/**
 * Convert string as received by regex parsing to associated array
 */
function map_key_values($content_string, &$arr) {

  // Split by newline into different pairs
  $temp = preg_split("/\r\n|\n|\r/", $content_string);

  // Add pairs to the associated array if they are not parantheses
  foreach ($temp as $pair) {
    if (trim($pair) == "(" or trim($pair) == ")")
      continue;
    $pair = array_map("trim", preg_split("/ +/", $pair, 2));
    $pair[1] = remove_quotes($pair[1]);

    // Handle duplicate keys (if the key is rom) and add values to a arary instead
    if ($pair[0] == "rom") {
      if (array_key_exists($pair[0], $arr)) {
        array_push($arr[$pair[0]], map_checksum_data($pair[1]));
      }
      else {
        $arr[$pair[0]] = array(map_checksum_data($pair[1]));
      }
    }
    else {
      $arr[$pair[0]] = stripslashes($pair[1]);
    }
  }
}

/**
 * Parse DAT file and separate the contents each segment into an array
 * Segments are of the form `scummvm ( )`, `game ( )` etc.
 */
function match_outermost_brackets($input) {
  $matches = array();
  $depth = 0;
  $inside_quotes = false;
  $cur_index = 0;

  for ($i = 0; $i < strlen($input); $i++) {
    $char = $input[$i];

    if ($char == '(' && !$inside_quotes) {
      if ($depth === 0) {
        $cur_index = $i;
      }
      $depth++;
    }
    elseif ($char == ')' && !$inside_quotes) {
      $depth--;
      if ($depth === 0) {
        $match = substr($input, $cur_index, $i - $cur_index + 1);
        array_push($matches, array($match, $cur_index));
      }
    }
    elseif ($char == '"' && $input[$i - 1] != '\\') {
      $inside_quotes = !$inside_quotes;
    }
  }

  return $matches;
}

/**
 * Take DAT filepath as input and return parsed data in the form of
 * associated arrays
 */
function parse_dat($dat_filepath) {
  $dat_file = fopen($dat_filepath, "r") or die("Unable to open file!");
  $content = fread($dat_file, filesize($dat_filepath));
  fclose($dat_file);

  if (!$content) {
    error_log("File not readable");
  }

  $header = array();
  $game_data = array();
  $resources = array();

  $matches = match_outermost_brackets($content);
  if ($matches) {
    foreach ($matches as $data_segment) {
      if (strpos(substr($content, $data_segment[1] - 11, 11), "clrmamepro") !== false ||
        strpos(substr($content, $data_segment[1] - 8, 8), "scummvm") !== false) {
        map_key_values($data_segment[0], $header);
      }
      elseif (strpos(substr($content, $data_segment[1] - 5, $data_segment[1]), "game") !== false) {
        $temp = array();
        map_key_values($data_segment[0], $temp);
        array_push($game_data, $temp);
      }
      elseif (strpos(substr($content, $data_segment[1] - 9, $data_segment[1]), "resource") !== false) {
        $temp = array();
        map_key_values($data_segment[0], $temp);
        $resources[$temp["name"]] = $temp;
      }
    }

  }

  // Print statements for debugging
  // Uncomment to see parsed data

  // echo "<pre>";
  // print_r($header);
  // print_r($game_data);
  // print_r($resources);
  // echo "</pre>";

  return array($header, $game_data, $resources, $dat_filepath);
}

/**
 * Retrieves the checksum and checktype of a given type + checksum
 * eg: md5-5000 t:12345... -> 5000, md5-t, 12345...
 */
function get_checksum_props($checktype, $checksum) {
  $checksize = 0;
  if (strpos($checktype, '-') !== false) {
    $checksize = explode('-', $checktype)[1];
    $checktype = explode('-', $checktype)[0];
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

    $records = $conn->query(sprintf("SELECT file.fileset
    FROM filechecksum
    JOIN file ON filechecksum.file = file.id
    WHERE filechecksum.checksum = '%s' AND file.detection = TRUE", $checksum));
    $records = $records->fetch_all();

    // If file is not part of detection entries, skip it
    if (count($records) == 0)
      continue;

    $matches_count++;
    foreach ($records as $record)
      array_push($matching_filesets, $record[0]);
  }

  // Check if there is a fileset_id that is present in all results
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

  return $matching_games;
}

/**
 * Routine for inserting a game into the database, inserting into engine and
 * game tables
 */
function insert_game($engineid, $title, $gameid, $extra, $platform, $lang, $conn) {
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
  VALUES (NULL, '%s')", $engineid);
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

/**
 * Inserting new fileset
 * Called for both detection entries and other forms of DATs
 */
function insert_fileset($src, $detection, $conn) {
  $status = $detection ? "detection" : $src;
  $game = "NULL";

  if ($detection) {
    $status = "detection";
    $game = "@game_last";
  }

  // $game should not be parsed as a mysql string, hence no quotes
  $query = sprintf("INSERT INTO fileset (game, status, src, `key`)
  VALUES (%s, '%s', '%s', NULL)", $game, $status, $src);
  $conn->query($query);
  $conn->query("SET @fileset_last = LAST_INSERT_ID()");
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
  if (isset($file["md5-5000"])) {
    $checksum = $file["md5-5000"];
  }
  else {
    foreach ($file as $key => $value) {
      if (strpos($key, "md5") !== false) {
        list($tmp1, $tmp2, $checksum) = get_checksum_props($key, $value);
        break;
      }
    }
  }

  $query = sprintf("INSERT INTO file (name, size, checksum, fileset, detection)
  VALUES ('%s', '%s', '%s', @fileset_last, %d)", mysqli_real_escape_string($conn, $file["name"]),
    $file["size"], $checksum, $detection);
  $conn->query($query);
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

  // Move files from the original fileset to the new fileset
  $conn->query(sprintf("UPDATE file
  SET fileset = %d
  WHERE fileset = %d", $dat_id, $detection_id));

  // Add fileset pair to history ($dat_id is the new fileset for $detection_id)
  $conn->query(sprintf("INSERT INTO history (`timestamp`, fileset, oldfileset)
  VALUES (FROM_UNIXTIME(%d), %d, %d)", time(), $dat_id, $detection_id));
  $conn->query("UPDATE history SET fileset = {$dat_id} WHERE fileset = {$detection_id}");

  // Delete original fileset
  $conn->query("DELETE FROM fileset WHERE id = {$detection_id}");

  if (!$conn->commit())
    echo "Error merging filesets";
}

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
 * Create an entry to the log table on each call of db_insert() or
 * populate_matching_games()
 */
function create_log($category, $user, $text) {
  $conn = db_connect();
  $conn->query(sprintf("INSERT INTO log (`timestamp`, category, user, `text`)
  VALUES (FROM_UNIXTIME(%d), '%s', '%s', '%s')", time(), $category, $user, $text));
  if (!$conn->commit())
    echo "Creating log failed<br/>";
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
   * src can be:
   *  detection -> Detection entries (source of truth)
   *  user -> Submitted by users via ScummVM, unmatched (Not used in the parser)
   *  scan -> Submitted by cli/scanner, unmatched
   *  dat -> Submitted by DAT, unmatched
   *  partialmatch -> Submitted by DAT, matched
   *  fullmatch -> Submitted by cli/scanner, matched
   */
  $src = "";
  if ($author == "scan" || $author == "scummvm")
    $src = $author;
  else
    $src = "dat";

  $detection = ($src == "scummvm");
  $status = $detection ? "detection" : $src;

  foreach ($game_data as $fileset) {
    if ($detection) {
      $engineid = $fileset["sourcefile"];
      $gameid = $fileset["name"];
      $title = $fileset["title"];
      $extra = $fileset["extra"];
      $platform = $fileset["platform"];
      $lang = $fileset["language"];

      insert_game($engineid, $title, $gameid, $extra, $platform, $lang, $conn);
    }
    elseif ($src == "dat")
      if (isset($resources[$fileset["romof"]]))
        $fileset["rom"] = array_merge($fileset["rom"], $resources[$fileset["romof"]]["rom"]);

    insert_fileset($src, $detection, $conn);
    calc_key($fileset["rom"]);
    foreach ($fileset["rom"] as $file) {
      insert_file($file, $detection, $src, $conn);
      foreach ($file as $key => $value) {
        if ($key != "name" && $key != "size")
          insert_filechecksum($file, $key, $conn);
      }
    }

    // Add key if uploaded DAT is of detection entries
    if ($detection) {
      $conn->query(sprintf("UPDATE fileset SET `key` = '%s' WHERE id = @fileset_last",
        calc_key($fileset["rom"])));
    }
  }
  $category_text = "Uploaded from " . $src . ", state '" . $status . "'";
  $log_text = sprintf("Loaded DAT file, filename \"%s\", size %d, author \"%s\", version %s",
    $filepath, filesize($filepath), $author, $version);

  if (!$conn->commit())
    echo "Inserting failed<br/>";
  else
    create_log(mysqli_real_escape_string($conn, $category_text), "unknown", mysqli_real_escape_string($conn, $log_text)); // FIXME: User name is "unknown"
}

function populate_matching_games() {
  $conn = db_connect();

  // Getting unmatched filesets
  $unmatched_filesets = array();

  $unmatched_files = $conn->query(sprintf("SELECT fileset.id, filechecksum.checksum, fileset.src from fileset
  JOIN file ON file.fileset = fileset.id
  JOIN filechecksum ON file.id = filechecksum.file
  WHERE fileset.game IS NULL"));
  $unmatched_files = $unmatched_files->fetch_all();

  // Splitting them into different filesets
  for ($i = 0; $i < count($unmatched_files); $i++) {
    $cur_fileset = $unmatched_files[$i][0];
    $src = $unmatched_files[$i][2];
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

    $category_text = "Matched, state '" . $status . "'";
    $log_text = "Matched game {$matched_game['engineid']}:
    {$matched_game['gameid']}-{$matched_game['platform']}-{$matched_game['language']}
    variant {$matched_game['key']} from {$fileset[0][2]}.";

    // Updating the fileset.game value to be $matched_game["id"]
    $query = sprintf("UPDATE fileset
    SET game = %d, status = '%s', `key` = '%s'
    WHERE id = %d", $matched_game["id"], $status, $matched_game["key"], $fileset[0][0]);
    merge_filesets($matched_game["fileset"], $fileset[0][0]);

    if ($conn->query($query))
      create_log(mysqli_real_escape_string($conn, $category_text), "unknown",
        mysqli_real_escape_string($conn, $log_text)); // FIXME: user name is unknown

    if (!$conn->commit())
      echo "Updating matched games failed<br/>";
  }
}

// Process command line args
if ($index = array_search("--upload", $argv)) {
  foreach (array_slice($argv, $index + 1) as $filepath) {
    if ($filepath == "--match")
      continue;

    db_insert(parse_dat($filepath));
  }
}

if (in_array("--match", $argv)) {
  populate_matching_games();
}

?>

