<!DOCTYPE html>
<html lang="en">

<head>
  <title>ImageDiff</title>

  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="stylesheet" type="text/css" href="assets/styles/main.css" />

  <?php require __DIR__ . '/src/file_browser.php' ?>
</head>

<body>
  <div class="file-browser">
    <?php displayDir(isset($_GET['dir']) ? $_GET['dir'] : '.') ?>
  </div>
</body>

</html>
