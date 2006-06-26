<!-- DEBUG: privmsgs_body.tpl starts here -->

<script language="Javascript" type="text/javascript">
	//
	// Should really check the browser to stop this whining ...
	//
	function select_switch(status)
	{
		for (i = 0; i < document.privmsg_list.length; i++)
		{
			document.privmsg_list.elements[i].checked = status;
		}
	}
</script>

<table border="0" cellspacing="0" cellpadding="0" align="center" width="98%">
  <tr> 
	<td align="left" width="20%"></td>	
	<td valign="middle" align="center" width="60%"> 
	  <table cellspacing="2" cellpadding="2" border="0" align="center">
		<tr style="vertical-align: middle;"> 
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
	</td>
	<td align="right" width="20%"> 
	  <!-- BEGIN switch_box_size_notice -->
	  <table width="175" cellspacing="1" cellpadding="2" border="0">
		<tr> 
		  <td colspan="3" width="100%" class="row1" nowrap><span class="smalltext">{BOX_SIZE_STATUS}</span></td>
		</tr>
		<tr> 
		  <td colspan="3" width="100%" class="row1">
			<table cellspacing="0" cellpadding="1" border="0">
			  <tr> 
				<td class="toprow"><img src="templates/SVMDesign/images/spacer.gif" width="{INBOX_LIMIT_IMG_WIDTH}" height="8" alt="{INBOX_LIMIT_PERCENT}"></td>
			  </tr>
			</table>
		  </td>
		</tr>
		<tr> 
		  <td width="33%" class="row1"><span class="smalltext">0%</span></td>
		  <td width="34%" align="center" class="row1"><span class="smalltext">50%</span></td>
		  <td width="33%" align="right" class="row1"><span class="smalltext">100%</span></td>
		</tr>
	  </table>
	  <!-- END switch_box_size_notice -->
	</td>
  </tr>
</table>

<br clear="all">

<form method="post" name="privmsg_list" action="{S_PRIVMSGS_ACTION}">

        <table width="98%" cellspacing="7" cellpadding="1" border="0" align="center">
          <tr> 
			<td align="left" valign="middle" width="1%">{POST_PM_IMG}</td>	  
			<td align="right" nowrap>
				<span class="smalltext">{L_DISPLAY_MESSAGES}: 
					<select name="msgdays">{S_SELECT_MSG_DAYS}</select>
					<input type="submit" value="{L_GO}" name="submit_msgdays">
				</span>
			</td>
		</tr>
		</table>
		

<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">

        <table border="0" cellpadding="7" cellspacing="1" width="100%">
          <tr align="center"> 
            <td width="5%"height="35" class="toprow"><span class="toprowtext">&nbsp;{L_FLAG}&nbsp;</span></td>
	        <td width="55%"height="35" class="toprow"><span class="toprowtext">&nbsp;{L_SUBJECT}&nbsp;</span></td>
	        <td width="20%"height="35" class="toprow"><span class="toprowtext">&nbsp;{L_FROM_OR_TO}&nbsp;</span></td>
	        <td width="15%"height="35" class="toprow"><span class="toprowtext">&nbsp;{L_DATE}&nbsp;</span></td>
	        <td width="5%"height="35" class="toprow"><span class="toprowtext">&nbsp;{L_MARK}&nbsp;</span></td>
	</tr>
	<!-- BEGIN listrow -->
	<tr> 
	  <td width="5%" align="center" valign="middle" class="row1"><img src="{listrow.PRIVMSG_FOLDER_IMG}" alt="{listrow.L_PRIVMSG_FOLDER_ALT}"></td>
	  <td width="55%" valign="middle" class="row1"><span class="topictitle">&nbsp;<a href="{listrow.U_READ}" class="topiclink">{listrow.SUBJECT}</a></span></td>
	  <td width="20%" valign="middle" align="center" class="row1"><span class="name">&nbsp;<a href="{listrow.U_FROM_USER_PROFILE}" class="mediumlink">{listrow.FROM}</a></span></td>
	  <td width="15%" align="center" valign="middle" class="row1"><span class="smalltext">{listrow.DATE}</span></td>
	  <td width="5%" align="center" valign="middle" class="row1"><span class="smalltext"> 
		<input type="checkbox" name="mark[]2" value="{listrow.S_MARK_ID}">
		</span></td>
	</tr>
	<!-- END listrow -->
	<!-- BEGIN switch_no_messages -->
	<tr> 
	  <td class="row1" colspan="5" align="center" valign="middle"><span class="mediumtext">{L_NO_MESSAGES}</span></td>
	</tr>
	<!-- END switch_no_messages -->
	<tr> 
	  <td height="34" class="catrow" colspan="5" align="right"> {S_HIDDEN_FIELDS} 
		<input type="submit" name="save" value="{L_SAVE_MARKED}">
		&nbsp; 
		<input type="submit" name="delete" value="{L_DELETE_MARKED}">
		&nbsp; 
		<input type="submit" name="deleteall" value="{L_DELETE_ALL}">
	  </td>
	</tr>
  </table>
</td>
</tr>
</table>
  <table width="98%" cellspacing="2" border="0" align="center" cellpadding="2">
    <tr> 
      <td align="left" valign="middle" width="100%"><span class="smalltext">{PAGE_NUMBER}&nbsp;</span></td>
      <td align="right" valign="top" nowrap><b><span class="smalltext"><a href="javascript:select_switch(true);" class="smalllink">{L_MARK_ALL}</a> 
        :: <a href="javascript:select_switch(false);" class="smalllink">{L_UNMARK_ALL}</a></span></b><br>
        <span class="smalltext">{PAGINATION}<br>
        </span><span class="smalltext">{S_TIMEZONE}</span></td>
    </tr>
  </table>
</form>

<table width="98%" border="0" align="center">
  <tr> 
	<td align="right" valign="top">{JUMPBOX}</td>
  </tr>
</table>
