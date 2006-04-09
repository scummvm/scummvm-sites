<?php
// Standalone mockup of the ScummVM SF archives page.
// Most SQL calls replaced with dummy text to save fiddling with adding data.

define('IN_PHPBB', true);
$phpbb_root_path = './';
include($phpbb_root_path . 'extension.inc');
include($phpbb_root_path . 'common.'.$phpEx);

//
// Start session management
//
$userdata = session_pagestart($user_ip, PAGE_VIEWONLINE);
init_userprefs($userdata);
//
// End session management
//

$page_title = "Forum Archives from SourceForge";
include($phpbb_root_path . 'includes/page_header.'.$phpEx);

if ($_GET['thread']) {
	$template->set_filenames(array('body' => 'archives_post_body.tpl'));
	showThread($_GET['thread']);
} else if ($_GET['forum']) {
	$template->set_filenames(array('body' => 'archives_forum_body.tpl'));
	$template->assign_vars(array(
        	'L_TOPICS' => $lang['Topics'],
        	'L_REPLIES' => $lang['Replies'],
        	'L_VIEWS' => $lang['Views'],
        	'L_POSTS' => $lang['Posts'],
        	'L_LASTPOST' => $lang['Last_Post']));

	if ($_GET['forum'] == "general") {
		$template->assign_vars(array('FORUM_NAME' => "General Discussion"));
		browseForum(115756);
	} else if ($_GET['forum'] == "help") {
		$template->assign_vars(array('FORUM_NAME' => "Help"));
		browseForum(115757);
	} else {
		$html = "<H2>Invalid Forum</H2>";
		$template->assign_vars(array('FORUM_NAME' => "Error #1331", TOP_TEXT => $html));
	}
} else {
	$template->set_filenames(array('body' => 'archives_menu_body.tpl'));
	$html .= "
Select a forum:
<UL>
<LI><A HREF='archives.php?forum=general'>Old 'General Discussion' forum</A>
<LI><A HREF='archives.php?forum=help'>Old 'Help' forum</A>
</UL>";
	$template->assign_vars(array('FORUM_NAME' => "None", TOP_TEXT => $html));
}

$template->pparse('body');
include($phpbb_root_path . 'includes/page_tail.'.$phpEx);
exit(0);

function showThread($id) {
	global $theme, $template, $images, $lang, $db, $board_config;

	if ($row['FORUM_ID'] == 115756) {	
                $template->assign_vars(array('FORUM_NAME' => "General Discussion"));
		$forum_name = "general";
        } else if ($row['FORUM_ID'] == 115757) {
                $template->assign_vars(array('FORUM_NAME' => "Help"));
		$forum_name = "help";
        }

$template->assign_vars(array(
	'TOPIC_ID' => 1,
        'PAGINATION' => $pagination,
	'TOPIC_TITLE' => "Test Topic",
        'PAGE_NUMBER' => sprintf($lang['Page_of'], 1, 1),

        'L_AUTHOR' => $lang['Author'],
        'L_MESSAGE' => $lang['Message'],
        'L_POSTED' => $lang['Posted'],
        'L_POST_SUBJECT' => $lang['Post_subject'],
        'L_VIEW_NEXT_TOPIC' => $lang['View_next_topic'],
        'L_VIEW_PREVIOUS_TOPIC' => $lang['View_previous_topic'],
        'L_POST_NEW_TOPIC' => $post_alt,
        'L_POST_REPLY_TOPIC' => $reply_alt,
        'L_BACK_TO_TOP' => $lang['Back_to_top'],

        'S_TOPIC_LINK' => POST_TOPIC_URL,
        'S_SELECT_POST_DAYS' => $select_post_days,
        'S_SELECT_POST_ORDER' => $select_post_order,
        'S_AUTH_LIST' => $s_auth_can,
        'S_TOPIC_ADMIN' => $topic_mod,
        'S_WATCH_TOPIC' => $s_watching_topic,
        'S_WATCH_TOPIC_IMG' => $s_watching_topic_img,

        'U_VIEW_TOPIC' => append_sid("archives.php?thread=1"), 
        'U_VIEW_FORUM' => append_sid("archives.php?forum=$forum_name"))
	);

	$i = 0;
	while ($i < 5) {
		makePost($row);
		$i++;
	}
}

function makePost($row) {
	global $theme, $template, $images, $lang, $db, $board_config;

		$post_subject = "Subject";
		$post_author = "SSomeone Green <BR>(s1green)";
		$post_body = "Lots of <br>text and stuff which goes on a bit and rambles and I guess<br>I thought that Sam and Max was better of the two.";
		$poster_from = "SourceForge User";
        $post_date = create_date($board_config['default_dateformat'],$row['DATE'], $board_config['board_timezone']);
        $template->assign_block_vars('postrow', array(
                'ROW_COLOR' => '#' . $row_color,
                'ROW_CLASS' => $row_class,
                'POSTER_NAME' => $post_author,
                'POSTER_RANK' => $poster_rank,
                'RANK_IMAGE' => $rank_image,
                'POSTER_JOINED' => $poster_joined,
                'POSTER_POSTS' => $poster_posts,
                'POSTER_FROM' => $poster_from,
                'POST_DATE' => $post_date,
                'POST_SUBJECT' => "Post Subject",
                'MESSAGE' => "This is filler text.<br>This is filler text.<br>",
                'SIGNATURE' => $user_sig,
                'MINI_POST_IMG' => $mini_post_img,

                'L_MINI_POST_ALT' => $mini_post_alt,

                'U_MINI_POST' => $mini_post_url,
                'U_POST_ID' => $row['MSG_ID'])
        );
}

function browseForum($id) {
	global $theme, $template, $images, $db, $board_config;
	$i = 0;
	$end = 0;
	$start = intval($_GET['start']);

	$count = 20;	// Number of posts

	$pagination = generate_pagination("archives.php?forum={$_GET['forum']}", 
$count['count'], $board_config['posts_per_page'], (int)$_GET['start']);
$template->assign_vars(array(
        'PAGINATION' => $pagination,
        'PAGE_NUMBER' => sprintf($lang['Page_of'], 1, 1),
	));
	$limit = "$start, {$board_config['posts_per_page']} ";

	while($i< 20) {
		$topic_title = "Title";
		$topic_author = "Poster Name";
		$last_post_time = create_date($board_config['default_dateformat'],$last_row['date'], $board_config['board_timezone']);
		$first_post_time = create_date($board_config['default_dateformat'],$row['date'], $board_config['board_timezone']);

                $row_color = ( !($i % 2) ) ? $theme['td_color1'] : $theme['td_color2'];
                $row_class = ( !($i % 2) ) ? $theme['td_class1'] : $theme['td_class2'];
                $template->assign_block_vars('topicrow', array(
                        'ROW_COLOR' => $row_color,
                        'ROW_CLASS' => $row_class,
                        'FORUM_ID' => 2,
                        'TOPIC_ID' => 1,
                        'TOPIC_FOLDER_IMG' => $images['folder_locked'],
                        'TOPIC_AUTHOR' => $topic_author,
                        'GOTO_PAGE' => "",
                        'REPLIES' => 99,
                        'NEWEST_POST_IMG' => $newest_post_img,
                        'TOPIC_TITLE' => $topic_title,
                        'TOPIC_TYPE' => "",
                        'FIRST_POST_TIME' => $first_post_time,
                        'LAST_POST_TIME' => $last_post_time,
                        'LAST_POST_AUTHOR' => "",
                        'LAST_POST_IMG' => $last_post_url,
                        'L_TOPIC_FOLDER_ALT' => $folder_alt,
                        'U_VIEW_TOPIC' => append_sid("archives.php?thread=1"))
                );
		$i++;
		}
		$end = $row['start'];
}

function nl2br_mine($string){
    // replace any newlines that aren't preceded by a > with a <br />
    $string = preg_replace('/(?<!>)\n/', "<br />\n", $string);
 
    return $string;
 }
?>
