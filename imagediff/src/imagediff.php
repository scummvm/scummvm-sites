<?php
header('Content-Type: image/png');
function pixelDiff(GDImage &$res, int $pixel1, int $pixel2) {
    $r1 = ($pixel1 >> 16) & 0xFF;
    $g1 = ($pixel1 >> 8) & 0xFF;
    $b1 = $pixel1 & 0xFF;

    $r2 = ($pixel2 >> 16) & 0xFF;
    $g2 = ($pixel2 >> 8) & 0xFF;
    $b2 = $pixel2 & 0xFF;

    $r = abs($r1 - $r2);
    $g = abs($g1 - $g2);
    $b = abs($b1 - $b2);

    return imagecolorallocate($res, $r, $g, $b);
}

function imageDiff($path1, $path2) {
    $img1 = imagecreatefrompng($path1);
    $img2 = imagecreatefrompng($path2);
    $width = imagesx($img1);
    $height = imagesy($img1);

    $res = @imagecreatetruecolor($width, $height)
        or die("Cannot Initialize new GD image stream");
    $bg = imagecolorallocate($res, 0, 0, 0);

    for ($i = 0; $i < $width; $i++) {
        for ($j = 0; $j < $height; $j++) {
            imagesetpixel($res, $i, $j, pixelDiff(
                $res,
                imagecolorat($img1, $i, $j),
                imagecolorat($img2, $i, $j)
            ));
        }
    }
    ob_start();

    imagepng($res);
    $image_data = ob_get_contents();
    imagedestroy($res);

    ob_end_clean();

    return base64_encode($image_data);
}

imageDiff("../assets/1.png", "../assets/2.png");
?>

