<?php
include_once(__DIR__.'/app/app.php');
include_once(__DIR__.'/app/lib/Cache.php');

if ($Planet->loadOpml(__DIR__.'/custom/people.opml') == 0) exit;

$Planet->loadFeeds();
$items = $Planet->getItems();
$limit = $PlanetConfig->getMaxDisplay();
$count = 0;

header('Content-Type: text/xml; charset=UTF-8');
echo '<?xml version="1.0" encoding="UTF-8" ?>';
?>
<rss version="2.0">
	<channel>
		<title><?=htmlspecialchars($PlanetConfig->getName())?></title>
		<link><?=$PlanetConfig->getUrl()?></link>
		<language>en</language>
    <description><?=htmlspecialchars($PlanetConfig->getName())?> - <?=$PlanetConfig->getUrl()?></description>
		<?php $count = 0; ?>
    <?php foreach ($items as $item): ?>
		<item>
			<title><?=htmlspecialchars($item->get_feed()->getName())?> : <?=htmlspecialchars($item->get_title())?></title>
			<guid><?=htmlspecialchars($item->get_permalink())?></guid>
      <link><?=htmlspecialchars($item->get_permalink())?>/</link>
      <description><![CDATA[<?=$item->get_content()?>]]></description>
			<pubDate><?=$item->get_date(DATE_RSS)?></pubDate>
			<author>nospam@scummvm.org (<?=($item->get_author() ? strip_tags($item->get_author()->get_name()) : 'anonymous')?>)</author>
		</item>
		<?php if (++$count == $limit) break; ?>
    <?php endforeach; ?>
	</channel>
</rss>
