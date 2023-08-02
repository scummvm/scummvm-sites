<?php
require 'include/db_functions.php';

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

function user_insert_fileset($user_fileset, $conn) {
  $src = 'user';
  $detection = 'false';
  $key = '';
  $megakey = user_calc_key($user_fileset);
  $transaction_id = $conn->query("SELECT MAX(`transaction`) FROM transactions")->fetch_array()[0] + 1;
  $log_text = "from user submitted files";
  $conn = db_connect();

  if (insert_fileset($src, $detection, $key, $megakey, $transaction_id, $log_text, $conn)) {
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
?>

