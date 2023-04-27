<link rel="stylesheet" type="text/css" href="../assets/styles/main.css" />

<?php
require __DIR__ . "/imagediff.php";

$src_img_path = isset($_GET['image']) ? $_GET['image'] : '';
if (!$src_img_path) {
  echo "<h2>Invalid Image</h2>";
}

$path_parts = explode(DIRECTORY_SEPARATOR, $src_img_path);
$target_dir = join("/", array_slice($path_parts, 0, count($path_parts) - 2));
$src_filename = end($path_parts);

$builds = scandir($target_dir);
rsort($builds);

$loop_count = 0;
foreach ($builds as $build) {
  $build_path = $target_dir . "/" . $build;
  if (!is_dir($build_path) or in_array($build, array(".", "..")))
    continue;

  $files = scandir($build_path);

  foreach ($files as $file) {
    if ($loop_count >= 3)
      break;

    $cmp_img_path = $build_path . "/" . $file;
    if ($file == $src_filename and $cmp_img_path != $src_img_path) {
      $res = image_diff($src_img_path, $cmp_img_path);
      // error_log("<img class=\"compare\" src=\"" . get_relative_path(realpath("./"), $cmp_img_path) . "\" />");

      echo "<img class=\"compare\" src=\"data:image/png;base64," .
        base64_encode(file_get_contents($src_img_path)) . "\" />";
      echo "<img class=\"compare\" src=\"data:image/png;base64," . $res . "\" />";
      echo "<img class=\"compare\" src=\"data:image/png;base64," .
        base64_encode(file_get_contents($cmp_img_path)) . "\" />";
      echo "<p />";

      $loop_count++;
    }
  }
}

?>

