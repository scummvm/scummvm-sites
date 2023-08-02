<?php

$request = $_SERVER['REQUEST_URI'];
$api_root = '/endpoints/';

switch ($request) {
  case '':
  case '/':
    require __DIR__ . '/index.html';
    break;

  case '/api/validate':
    require __DIR__ . $api_root . 'validate.php';
}
?>
