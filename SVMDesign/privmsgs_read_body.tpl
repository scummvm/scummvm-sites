<!-- DEBUG: privmsgs_read_body.tpl starts here -->
<table cellspacing="2" cellpadding="2" border="0" align="center">
  <tr> 
		<td>{INBOX_IMG}</td>
		<td><span class="smalltext">{INBOX}&nbsp;&nbsp;</span></td>
		<td>{SENTBOX_IMG}</td>
		<td><span class="smalltext">{SENTBOX}&nbsp;&nbsp;</span></td>
		<td>{OUTBOX_IMG}</td>
		<td><span class="smalltext">{OUTBOX}&nbsp;&nbsp;</span></td>
		<td>{SAVEBOX_IMG}</td>
		<td><span class="smalltext">{SAVEBOX}&nbsp;&nbsp;</span></td>
  </tr>
</table>

<br clear="all" />

<form method="post" action="{S_PRIVMSGS_ACTION}">
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">

<table border="0" cellpadding="4" cellspacing="1" width="100%" class="forumline">
	<tr> 
	  <th colspan="3" class="toprow"><span class="toprowtext">{BOX_NAME} :: {L_MESSAGE}</span></th>
	</tr>
	<tr> 
	  <td class="row1"><span class="mediumtext">{L_FROM}:</span></td>
	  <td width="100%" class="row1" colspan="2"><span class="mediumtext">{MESSAGE_FROM}</span></td>
	</tr>
	<tr> 
	  <td class="row1"><span class="mediumtext">{L_TO}:</span></td>
	  <td width="100%" class="row1" colspan="2"><span class="mediumtext">{MESSAGE_TO}</span></td>
	</tr>
	<tr> 
	  <td class="row1"><span class="mediumtext">{L_POSTED}:</span></td>
	  <td width="100%" class="row1" colspan="2"><span class="mediumtext">{POST_DATE}</span></td>
	</tr>
	<tr> 
	  <td class="row1"><span class="mediumtext">{L_SUBJECT}:</span></td>
	  <td nowrap width="100%" class="row1"><span class="mediumtext">{POST_SUBJECT}</span></td>
	  <td class="row1" align="right"> {QUOTE_PM_IMG} {EDIT_PM_IMG}</td>
	</tr>
	<tr> 
	  <td valign="top" colspan="3" class="row1"><span class="mediumtext">{MESSAGE}</span></td>
	</tr>
	<tr> 
	  <td width="78%" height="28" valign="bottom" colspan="3" class="row1"> 
		<table cellspacing="0" cellpadding="0" border="0" height="18">
		  <tr> 
			<td valign="middle" nowrap="nowrap">{PROFILE_IMG} {PM_IMG} {EMAIL_IMG} 
			  {WWW_IMG} {AIM_IMG} {YIM_IMG} {MSN_IMG}</td><td>&nbsp;</td><td valign="top" nowrap="nowrap"><script language="JavaScript" type="text/javascript"><!-- 

		if ( navigator.userAgent.toLowerCase().indexOf('mozilla') != -1 && navigator.userAgent.indexOf('5.') == -1 )
			document.write('{ICQ_IMG}');
		else
			document.write('<div style="position:relative"><div style="position:absolute">{ICQ_IMG}</div><div style="position:absolute;left:3px">{ICQ_STATUS_IMG}</div></div>');
		  
		  //--></script><noscript>{ICQ_IMG}</noscript></td>
		  </tr>
		</table>
	  </td>
	</tr>
	<tr>
	  <td class="catrow" colspan="3" align="right"> {S_HIDDEN_FIELDS} 
		<input type="submit" name="save" value="{L_SAVE_MSG}" class="liteoption" />
		&nbsp; 
		<input type="submit" name="delete" value="{L_DELETE_MSG}" class="liteoption" />
	  </td>
	</tr>
  </table>
  
 
  </td>
	</tr>
  </table>

  <table width="98%" cellspacing="0" border="0" align="center" cellpadding="2">
	<tr> 
	  <td>{REPLY_PM_IMG}</td>
	  <td align="right" valign="middle"><span class="mediumtextsmall">{S_TIMEZONE}</span></td>
	</tr>
  </table>


</form>

<table width="98%" cellspacing="2" border="0" align="center" cellpadding="2">
  <tr> 
	<td valign="top" align="right">{JUMPBOX}</td>
  </tr>
</table>
