<?php

require __DIR__ . '/../include/db_functions.php';
ini_set('memory_limit', '512M');

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

    if ($temp[$i] == 'crc' || $temp[$i] == 'sha1')
      continue;

    $temp[$i + 1] = remove_quotes($temp[$i + 1]);
    if ($temp[$i + 1] == ')')
      $temp[$i + 1] = "";
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

