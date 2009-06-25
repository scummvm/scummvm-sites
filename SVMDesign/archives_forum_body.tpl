<!-- DEBUG: archives_forum_body.tpl starts here --> 
<form method="post" action="{S_POST_DAYS_ACTION}">
  <table cellpadding="2" cellspacing="0" border="0" width="98%"  align="center">
    <tr> 
      <td valign="top" width="50%"><img src="templates/LastCrusade/images/folder_new.gif" border="0" align="absmiddle"> 
        <span class="largetext"><a href="index.php" class="largelink"><b>{SITENAME}</b></a> &gt; 
        <b>Archives: {FORUM_NAME}</b></a></span><br>
        <br>
	{TOP_TEXT}
      </td>
	<td align="right">
<b><span class="smalltext">{PAGINATION} </span></b>
	</td>
    </tr>
  </table>
  <table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
    <tr> 
      <td class="tableborder"> 
        <table cellpadding="4" cellspacing="1" border="0"  width="100%">
          <tr align="center"> 
            <td align="center" nowrap colspan="2" class="toprow" valign="middle">Thread</td>
            <td nowrap class="toprow" valign="middle"><span class="toprowtext">&nbsp;Thread 
              Starter&nbsp;</span></td>
            <td nowrap class="toprow" valign="middle"><span class="toprowtext">&nbsp;{L_REPLIES}&nbsp;</span></td>
            <td nowrap class="toprow" valign="middle"><span class="toprowtext">&nbsp;{L_VIEWS}&nbsp;</span></td>
            <td nowrap class="toprow" valign="middle"><span class="toprowtext">&nbsp;{L_LASTPOST}&nbsp;</span></td>
          </tr>
          <!-- BEGIN topicrow -->
          <tr align="center"> 
            <td class="row1" valign="middle"><img src="{topicrow.TOPIC_FOLDER_IMG}" alt="{topicrow.L_TOPIC_FOLDER_ALT}" title="{topicrow.L_TOPIC_FOLDER_ALT}"></td>
            <td align="left" class="row3" width="100%"><span class="smalltext">{topicrow.NEWEST_POST_IMG}{topicrow.TOPIC_TYPE}<a href="{topicrow.U_VIEW_TOPIC}" class="topiclink">{topicrow.TOPIC_TITLE}</a></span><span class="smalltext"><br>
              {topicrow.GOTO_PAGE}</span></td>
            <td nowrap class="row1"><span class="smalltext">{topicrow.TOPIC_AUTHOR}</span></td>
            <td class="row3" nowrap><span class="mediumtext">{topicrow.REPLIES}</span></td>
            <td class="row1" nowrap><span class="mediumtext">{topicrow.VIEWS}</span></td>
            <td class="row3" align="right" nowrap><span class="smalltext">{topicrow.LAST_POST_TIME}<br>{topicrow.LAST_POST_AUTHOR} {topicrow.LAST_POST_IMG}</span></td>
          </tr>
          <!-- END topicrow -->
          <!-- BEGIN switch_no_topics -->
          <tr align="center"> 
            <td colspan="6" class="row1">Crap! Post some topics 
              already and let the discussion begin!</td>
          </tr>
          <!-- END switch_no_topics -->
        </table>
      </td>
    </tr>
  </table>
  <table cellpadding="2" cellspacing="0" border="0" width="98%"  align="center">
    <tr valign="top"> 
      <td><a href="{U_POST_NEW_TOPIC}"><br>
        <img src="{POST_IMG}" border="0" alt="{L_POST_NEW_TOPIC}"></a><br>
        <span class="smalltext">
        {S_WATCH_FORUM}<br><a href="{U_MARK_READ}">{L_MARK_TOPICS_READ}</a></span></td>
      <td align="right"><span class="smalltext">{PAGE_NUMBER}<br>
        </span><span class="nav">{PAGINATION}</span><span class="smalltext"><br>
        {S_TIMEZONE} </span></td>
    </tr>
  </table>
  </form>
  <table cellpadding="2" cellspacing="0" border="0" width="98%"  align="center">
  <tr> 
    <td colspan="2" align="center"><span class="smalltext">{S_TIMEZONE}. </span> 
      <span class="smalltext">{CURRENT_TIME}</span> </td>
  </tr>
  <tr> 
    <td rowspan="2">
      <table border="0" cellspacing="2" cellpadding="2" align="center">
        <tr> 
          <td nowrap>(&nbsp;<img src="templates/LastCrusade/images/folder_new.gif" alt="{L_NEW_POSTS}" align="absmiddle" >&nbsp;{L_NEW_POSTS}&nbsp;&nbsp;)</td>
          <td nowrap>( <img src="templates/LastCrusade/images/folder_new_hot.gif" alt="{L_NEW_POSTS_HOT}" align="absmiddle" >&nbsp;{L_NEW_POSTS_HOT} 
            )&nbsp;&nbsp;</td>
          <td nowrap>( <img src="templates/LastCrusade/images/folder_lock.gif" alt="{L_NO_NEW_POSTS_TOPIC_LOCKED}" align="absmiddle" >&nbsp;Closed 
            thread )</td>
        </tr>
        <tr> 
          <td nowrap>(&nbsp;<img src="templates/LastCrusade/images/folder.gif" alt="{L_NO_NEW_POSTS}" align="absmiddle" >&nbsp;{L_NO_NEW_POSTS}&nbsp;)&nbsp;</td>
          <td nowrap colspan="2">( <img src="templates/LastCrusade/images/folder_hot.gif" alt="{L_NO_NEW_POSTS_HOT}" align="absmiddle" >&nbsp;{L_NO_NEW_POSTS_HOT} 
            )&nbsp;&nbsp;</td>
        </tr>
      </table>
    </td>
  </tr>
  <tr> </tr>
</table>
