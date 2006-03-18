<!-- DEBUG: search_results_posts.tpl starts here -->
 
<table width="98%" cellspacing="2" cellpadding="2" border="0" align="center">
  <tr> 
	  <td><img src="templates/SVMDesign/images/folder_new.gif" border="0" alt="Folder"></td>
      <td style="vertical-align: middle;" width="100%"><span class="largetext"><a href="index.php" class="largelink"><b>{SITENAME} 
      Forum Index</b></a></span></td>
  </tr>
  <tr>
	<td align="center" valign="middle" colspan="2"><span class="largetext"><b>{L_SEARCH_MATCHES}</b></span></td>
  </tr>
</table>
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
<table border="0" cellpadding="3" cellspacing="1" width="100%" class="forumline" align="center">
  <tr align="center"> 
          <td width="22%" class="toprow"><span class="toprowtext">{L_AUTHOR}</span></td>
	<td class="toprow"><span class="toprowtext">{L_MESSAGE}</span></td>
  </tr>
  <!-- BEGIN searchresults -->
  <tr> 
	<td colspan="2" class="row1">
		<table border="0" cellpadding="0" cellspacing="0">
			<tr>
	  <td><img src="templates/SVMDesign/images/folder.gif" border="0" alt="Folder"></td>
      <td style="vertical-align: middle;" width="100%">
      <span class="mediumtext">&nbsp;&nbsp;{L_TOPIC}:&nbsp;<a href="{searchresults.U_TOPIC}" class="topiclink">{searchresults.TOPIC_TITLE}</a></span></td>
			</tr>
		</table>
	</td>
  </tr>
  <tr> 
	<td width="22%" align="left" valign="top" class="row1" rowspan="2"><span class="smalltext"><b><a href="{searchresults.U_USER_PROFILE}" class="smalllink"></a>{searchresults.POSTER_NAME}</b></span><br />
	  <br />
	  <span class="smalltext">{L_REPLIES}: <b>{searchresults.TOPIC_REPLIES}</b><br />
	  {L_VIEWS}: <b>{searchresults.TOPIC_VIEWS}</b></span><br />
	</td>
	<td valign="top" class="row1"> <img src="templates/SVMDesign/images/icon_minipost.gif" alt="{searchresults.L_MINI_POST_ALT}"><span class="smalltext">{L_FORUM}:&nbsp;<b><a href="{searchresults.U_FORUM}" class="smalllink">{searchresults.FORUM_NAME}</a></b>&nbsp;&nbsp;&nbsp;{L_POSTED}: 
	  {searchresults.POST_DATE}&nbsp;&nbsp;&nbsp;Subject: <b><a href="{searchresults.U_POST}">{searchresults.POST_SUBJECT}</a></b></span></td>
  </tr>
  <tr>
	<td valign="top" class="row1"><span class="mediumtext">{searchresults.MESSAGE}</span></td>
  </tr>
  <!-- END searchresults -->
  <tr> 
	<td class="catrow" colspan="2" height="28" align="center">&nbsp; </td>
  </tr>
</table>
</td>
</tr>
</table>
<table width="98%" cellspacing="2" border="0" align="center" cellpadding="2">
  <tr> 
	<td align="left" valign="top"><span class="smalltext">{PAGE_NUMBER}</span></td>
	<td align="right" valign="top" nowrap><span class="smalltext">{PAGINATION}</span><br /><span class="smalltext">{S_TIMEZONE}</span></td>
  </tr>
</table>

<table width="98%" cellspacing="2" border="0" align="center">
  <tr> 
	<td valign="top" align="right">{JUMPBOX}</td>
  </tr>
</table>
