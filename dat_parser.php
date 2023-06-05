<?php

$dat_filepath = "ngi.dat";

$dat_file = fopen($dat_filepath, "r") or die("Unable to open file!");
$content = fread($dat_file, filesize($dat_filepath));

if (!$content) {
  error_log("File not readable");
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
      if ($arr[$pair[0]]) {
        array_push($arr[$pair[0]], $pair[1]);
      }
      else {
        $arr[$pair[0]] = array($pair[1]);
      }
    }
    else {
      $arr[$pair[0]] = $pair[1];
    }
  }
}

$header = array();
$game_data = array();
$resources = array();

$matches = array();
$header_exp = '/\((?:[^)(]+|(?R))*+\)/u'; // Get content inside outermost brackets
if (preg_match_all($header_exp, $content, $matches, PREG_OFFSET_CAPTURE)) {
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

fclose($dat_file);
?>

