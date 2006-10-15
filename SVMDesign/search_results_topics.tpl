<!-- DEBUG: search_results_topics.tpl starts here --> 
<table width="98%" cellspacing="2" cellpadding="2" border="0" align="center">
  <tr> 
	<td align="center" valign="middle"><span class="largetext"><b>{L_SEARCH_MATCHES}</b></span></td>
  </tr>
</table>

<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
      <table width="100%" cellpadding="4" cellspacing="1" border="0" class="forumline" align="center">
        <tr align="center"> 
          <td width="4%" class="toprow"><span class="toprowtext">&nbsp;</span></td>
	      <td class="toprow"><span class="toprowtext">&nbsp;{L_FORUM}&nbsp;</span></td>
	      <td class="toprow"><span class="toprowtext">&nbsp;{L_TOPICS}&nbsp;</span></td>
	      <td class="toprow"><span class="toprowtext">&nbsp;{L_AUTHOR}&nbsp;</span></td>
	      <td class="toprow"><span class="toprowtext">&nbsp;{L_REPLIES}&nbsp;</span></td>
	      <td class="toprow"><span class="toprowtext">&nbsp;{L_VIEWS}&nbsp;</span></td>
	      <td class="toprow"><span class="toprowtext">&nbsp;{L_LASTPOST}&nbsp;</span></td>
  </tr>
  <!-- BEGIN searchresults -->
  <tr> 
	<td class="row1" align="center" valign="middle"><img src="{searchresults.TOPIC_FOLDER_IMG}" width="19" height="18" alt="{searchresults.L_TOPIC_FOLDER_ALT}" title="{searchresults.L_TOPIC_FOLDER_ALT}" /></td>
	<td class="row1"><span class="smalltext"><a href="{searchresults.U_VIEW_FORUM}" class="forumlink">{searchresults.FORUM_NAME}</a></span></td>
	<td class="row1"><span class="smalltext">{searchresults.NEWEST_POST_IMG}{searchresults.TOPIC_TYPE}<a href="{searchresults.U_VIEW_TOPIC}" class="topiclink">{searchresults.TOPIC_TITLE}</a></span><br /><span class="smalltext">{searchresults.GOTO_PAGE}</span></td>
	<td class="row1" align="center" valign="middle"><span class="smalltext"><a href="{searchresults.U_TOPIC_POSTER_PROFILE}" class="smalllink">{searchresults.TOPIC_AUTHOR}</a></span></td>
	<td class="row1" align="center" valign="middle"><span class="smalltext">{searchresults.REPLIES}</span></td>
	<td class="row1" align="center" valign="middle"><span class="smalltext">{searchresults.VIEWS}</span></td>
	<td class="row1" align="center" valign="middle" nowrap><span class="smalltext">{searchresults.LAST_POST_TIME}<br />{searchresults.LAST_POST_AUTHOR} {searchresults.LAST_POST_IMG}</span></td>
  </tr>
  <!-- END searchresults -->
  <tr> 
	<td class="catrow" colspan="7" valign="middle">&nbsp; </td>
  </tr>
</table>
</td>
</tr>
</table>
<table width="98%" cellspacing="2" border="0" align="center" cellpadding="2">
  <tr> 
	<td align="left" valign="top"><span class="nav">{PAGE_NUMBER}</span></td>
	<td align="right" valign="top" nowrap><span class="nav">{PAGINATION}</span><br />{S_TIMEZONE}</td>
  </tr>
</table>

<table width="98%" cellspacing="2" border="0" align="center">
  <tr> 
	<td valign="top" align="right">{JUMPBOX}</td>
  </tr>
</table>
