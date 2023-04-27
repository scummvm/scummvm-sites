<?php function displayDir($dir = './') { ?>
  <?php
  function file_sort($a, $b) {
    return ($cmp = is_dir($b) - is_dir($a)) ? $cmp : strcmp($a, $b);
  }

  $current_dir = realpath($dir);
  $dir_content = scandir($current_dir);
  usort($dir_content, 'file_sort');
  ?>

  <div>
    <?php
    $path_parts = explode(DIRECTORY_SEPARATOR, $current_dir);
    $breadcrumbs = '';
    foreach ($path_parts as $part) {
      if (!$part) {
        continue;
      }
      $breadcrumbs .= $part . DIRECTORY_SEPARATOR;
      echo DIRECTORY_SEPARATOR . '<a href="?dir=' . '/' . $breadcrumbs . '">' . $part . '</a>';
    }
    ?>
  </div>

  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Size</th>
      </tr>
    </thead>
    <tbody>
      <?php foreach ($dir_content as $item):

        if ($item == '.'):
          continue;
        endif;
        $item_path = $current_dir . DIRECTORY_SEPARATOR . $item;
        ?>
        <tr>
          <td>
            <?php if (is_dir($item_path)): ?>
              <a href="?dir=<?php echo $item_path; ?>">
                <?php echo $item; ?>
              </a>
            <?php elseif (getimagesize($item_path)): ?>
              <a href="src/display_images.php?image=<?php echo $item_path; ?>">
                <?php echo $item; ?>
              </a>
            <?php else: ?>
              <?php echo $item; ?>
            <?php endif; ?>
          </td>
          <td>
            <?php echo is_dir($item_path) ? '' : filesize($item_path) . ' b'; ?>
          </td>
        </tr>
      <?php endforeach; ?>
    </tbody>
  </table>
<?php } ?>

