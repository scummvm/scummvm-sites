<?php

$request = $_SERVER['REQUEST_URI'];
$api_root = '/endpoints/';

switch ($request) {
  case '':
  case '/':
    require $_SERVER['DOCUMENT_ROOT'] . '/index.html';
    break;

  case '/api/validate':
    require $_SERVER['DOCUMENT_ROOT'] . $api_root . 'validate.php';
}
?>
