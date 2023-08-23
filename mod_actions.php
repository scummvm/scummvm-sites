<?php
// require __DIR__ . '/include/pagination.php';

$stylesheet = 'style.css';
$jquery_file = 'https://code.jquery.com/jquery-3.7.0.min.js';
$js_file = 'js_functions.js';
echo "<link rel='stylesheet' href='{$stylesheet}'>\n";
echo "<script type='text/javascript' src='{$jquery_file}'></script>\n";
echo "<script type='text/javascript' src='{$js_file}'></script>\n";


// Dev Tools
echo "<h3>Developer Moderation Tools</h3>";
echo "<button id='delete-button' type='button' onclick='delete_id(0)'>Delete filesets from last uploaded DAT</button>";
echo "<br/>";
echo "<button id='match-button' type='button' onclick='match_id(0)'>Merge Uploaded Fileset</button>";
echo "<br/>";
echo "<button id='match-button' type='button' onclick='match_id(0)'>Merge User Fileset</button>";

if (isset($_POST['delete'])) {
}
if (isset($_POST['match'])) {
  // merge_user_filesets();
}

echo "<p id='delete-confirm' class='hidden'>Fileset marked for deletion</p>"; // Hidden
?>

