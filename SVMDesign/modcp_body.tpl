<!-- DEBUG: modcp_body.tpl starts here -->
<form method="post" action="{S_MODCP_ACTION}">
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
        <table width="100%" cellpadding="4" cellspacing="1" border="0" class="forumline">
          <tr> 
	  <td class="toprow" colspan="5" align="center"><span class="toprowtext">{L_MOD_CP}</span> 
	  </td>
	</tr>
	<tr> 
	  <td class="row1" colspan="5" align="center"><span class="mediumtext">{L_MOD_CP_EXPLAIN}</span></td>
	</tr>
	      <tr align="center"> 
            <td width="4%" class="toprow"><span class="toprowtext">&nbsp;</span></td>
	        <td class="toprow"><span class="toprowtext">&nbsp;{L_TOPICS}&nbsp;</span></td>
	        <td width="8%" class="toprow"><span class="toprowtext">&nbsp;{L_REPLIES}&nbsp;</span></td>
	        <td width="17%" class="toprow"><span class="toprowtext">&nbsp;{L_LASTPOST}&nbsp;</span></td>
	        <td width="5%" class="toprow"><span class="toprowtext">&nbsp;{L_SELECT}&nbsp;</span></td>
	</tr>

	<!-- BEGIN topicrow -->
	<tr> 
	  <td class="row1" align="center" valign="middle"><img src="{topicrow.TOPIC_FOLDER_IMG}" alt="{topicrow.L_TOPIC_FOLDER_ALT}" title="{topicrow.L_TOPIC_FOLDER_ALT}" /></td>
	  <td class="row1">&nbsp;<span class="smalltext">{topicrow.TOPIC_TYPE}<a href="{topicrow.U_VIEW_TOPIC}" class="topiclink">{topicrow.TOPIC_TITLE}</a></span></td>
	  <td class="row1" align="center" valign="middle"><span class="mediumlink">{topicrow.REPLIES}</span></td>
	  <td class="row1" align="center" valign="middle"><span class="mediumlink">{topicrow.LAST_POST_TIME}</span></td>
	  <td class="row1" align="center" valign="middle"> 
		<input type="checkbox" name="topic_id_list[]" value="{topicrow.TOPIC_ID}" />
	  </td>
	</tr>
	<!-- END topicrow -->
	<tr align="right"> 
	  <td class="catrow" colspan="5"> {S_HIDDEN_FIELDS} 
		<input type="submit" name="delete" class="liteoption" value="{L_DELETE}" />
		&nbsp; 
		<input type="submit" name="move" class="liteoption" value="{L_MOVE}" />
		&nbsp; 
		<input type="submit" name="lock" class="liteoption" value="{L_LOCK}" />
		&nbsp; 
		<input type="submit" name="unlock" class="liteoption" value="{L_UNLOCK}" />
	  </td>
	</tr>
  </table>
  </td>
  </tr>
  </table>
  
  <table width="98%" cellspacing="2" border="0" align="center" cellpadding="2">
    <tr> 
	<td align="left" valign="middle"><span class="nav">{PAGE_NUMBER}</span></td>
	<td align="right" valign="top" nowrap>{S_TIMEZONE}<br /><span class="nav">{PAGINATION}</span></td>
  </tr>
</table>
</form>
<table width="98%" border="0" cellspacing="0" cellpadding="0" align="center">
  <tr> 
	<td align="right">{JUMPBOX}</td>
  </tr>
</table>
