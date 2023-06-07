<?php

ini_set('memory_limit', '512M');

/**
 * Convert string of checksum data from rom into associated array
 * Returns array instead of updating one like map_key_values
 */
function map_checksum_data($content_string) {
  $arr = array();
  $temp = preg_split("/\s/", $content_string);

  for ($i = 1; $i < count($temp); $i += 2) {
    if ($temp[$i] == ')')
      continue;
    $arr[$temp[$i]] = $temp[$i + 1];
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

    // Remove quotes from value if they are present
    if ($pair[1][0] == "\"")
      $pair[1] = substr($pair[1], 1, -1);

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
      $arr[$pair[0]] = $pair[1];
    }
  }
}

/**
 * Take DAT filepath as input and return parsed data in the form of
 * associated arrays
 */
function parse_dat($dat_filepath) {
  $dat_file = fopen($dat_filepath, "r") or die("Unable to open file!");
  $content = fread($dat_file, filesize($dat_filepath));

  if (!$content) {
    error_log("File not readable");
  }

  $header = array();
  $game_data = array();
  $resources = array();

  $matches = array();
  $exp = '/\((?:[^)(]+|(?R))*+\)/u'; // Get content inside outermost brackets
  if (preg_match_all($exp, $content, $matches, PREG_OFFSET_CAPTURE)) {
    foreach ($matches[0] as $data_segment) {
      if (strpos(substr($content, $data_segment[1] - 11, $data_segment[1]), "clrmamepro") !== false) {
        map_key_values($data_segment[0], $header);
      }
      elseif (strpos(substr($content, $data_segment[1] - 5, $data_segment[1]), "game") !== false) {
        $temp = array();
        map_key_values($data_segment[0], $temp);
        array_push($game_data, $temp);
      }
      elseif (strpos(substr($content, $data_segment[1] - 9, $data_segment[1]), "resource") !== false) {
        map_key_values($data_segment[0], $resources);
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

  fclose($dat_file);

  return array($header, $game_data, $resources);
}

/**
 * Routine for inserting a file into the database, intserting into all
 * required tables
 * $file is an associated array (the contents of 'rom')
 * If checksum of the given checktype doesn't exists, silently fails
 */
function insert_file($file, $key, $conn, $checktype = "md5", $checksize = 0) {
  if (!array_key_exists($checktype, $file))
    return;

  $query = sprintf("INSERT INTO file (name, size, checksum)
  VALUES ('%s', '%s', '%s')", mysqli_real_escape_string($conn, $file["name"]),
    $file["size"], $file[$checktype]);
  $conn->query($query);
  $conn->query("SET @file_last = LAST_INSERT_ID()");

  $query = sprintf("INSERT INTO filechecksum (file, checksize, checktype, checksum)
  VALUES (@file_last, '%s', '%s', '%s')", $checksize, $checktype, $file[$checktype]);
  $conn->query($query);
  $conn->query("SET @filechecksum_last = LAST_INSERT_ID()");

  $query = sprintf("INSERT INTO fileset (game, file, status, `key`)
  VALUES (NULL, @file_last, 0, '%s')", $key);
  $conn->query($query);
  $conn->query("SET @fileset_last = LAST_INSERT_ID()");

  $query = "INSERT INTO fileset_detection (fileset, checksum)
  VALUES (@fileset_last, @filechecksum_last)";
  $conn->query($query);
}

/**
 * Insert values from the associated array into the DB
 * They will be inserted under gameid NULL as the game itself is unconfirmed
 */
function db_insert($data_arr) {
  $header = $data_arr[0];
  $game_data = $data_arr[1];
  $resources = $data_arr[2];

  $servername = "localhost";
  $username = "username";
  $password = "password";
  $dbname = "integrity";

  // Create connection
  $conn = new mysqli($servername, $username, $password);

  // Check connection
  if ($conn->connect_errno) {
    die("Connect failed: " . $conn->connect_error);
  }

  $conn->query("USE " . $dbname);

  // Remove "ScummVM" from engine name
  $engine_name = preg_split("/\s/", $header["name"]);
  array_shift($engine_name);
  $engine_name = implode(" ", $engine_name);

  $query = sprintf("INSERT INTO engine (name, engineid)
  VALUES ('%s', '1')", $engine_name);
  $conn->query($query);
  $conn->query("SET @engine_last = LAST_INSERT_ID()");

  foreach ($game_data as $fileset) {
    foreach ($fileset["rom"] as $file) {
      $key = NULL;
      insert_file($file, $key, $conn);
      insert_file($file, $key, $conn, "crc");
      insert_file($file, $key, $conn, "sha1");
    }
  }
}

// db_insert(parse_dat("ngi.dat"));

?>

