<!-- groupcp_info_body.tpl -->
<form method="post" action="{S_GROUPCP_ACTION}">
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
  <table width="100%" cellpadding="4" cellspacing="1" border="0">
	      <tr align="center"> 
            <td colspan="7" class="toprow"><span class="toprowtext">{L_GROUP_INFORMATION}</span></td>
	</tr>
	<tr> 
	  <td class="row1" width="20%"><span class="mediumtext">{L_GROUP_NAME}:</span></td>
	  <td class="row1"><span class="mediumtext"><b>{GROUP_NAME}</b></span></td>
	</tr>
	<tr> 
	  <td class="row1" width="20%"><span class="mediumtext">{L_GROUP_DESC}:</span></td>
	  <td class="row1"><span class="mediumtext">{GROUP_DESC}</span></td>
	</tr>
	<tr> 
	  <td class="row1" width="20%"><span class="mediumtext">{L_GROUP_MEMBERSHIP}:</span></td>
	  <td class="row1"><span class="mediumtext">{GROUP_DETAILS} &nbsp;&nbsp;
	  <!-- BEGIN switch_subscribe_group_input -->
	  <input type="submit" name="joingroup" value="{L_JOIN_GROUP}" />
	  <!-- END switch_subscribe_group_input -->
	  <!-- BEGIN switch_unsubscribe_group_input -->
	  <input type="submit" name="unsub" value="{L_UNSUBSCRIBE_GROUP}" />
	  <!-- END switch_unsubscribe_group_input -->
	  </span></td>
	</tr>
	<!-- BEGIN switch_mod_option -->
	<tr> 
	  <td class="row1" width="20%"><span class="mediumtext">{L_GROUP_TYPE}:</span></td>
	  <td class="row1"><span class="mediumtext"><span class="mediumtext"><input type="radio" name="group_type" value="{S_GROUP_OPEN_TYPE}" {S_GROUP_OPEN_CHECKED} /> {L_GROUP_OPEN} &nbsp;&nbsp;<input type="radio" name="group_type" value="{S_GROUP_CLOSED_TYPE}" {S_GROUP_CLOSED_CHECKED} />	{L_GROUP_CLOSED} &nbsp;&nbsp;<input type="radio" name="group_type" value="{S_GROUP_HIDDEN_TYPE}" {S_GROUP_HIDDEN_CHECKED} />	{L_GROUP_HIDDEN} &nbsp;&nbsp; <input type="submit" name="groupstatus" value="{L_UPDATE}" /></span></span></td>
	</tr>
	<!-- END switch_mod_option -->
  </table>
  </td>
  </tr>
  </table>
{S_HIDDEN_FIELDS}
</form>

<form method="post" action="{S_GROUPCP_ACTION}" name="post">
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
<table width="100%" cellpadding="4" cellspacing="1" border="0">
	<tr> 
	  <td class="toprow" height="25"><span class="toprowtext">{L_PM}</span></td>
	  <td class="toprow"><span class="toprowtext">{L_USERNAME}</span></td>
	  <td class="toprow"><span class="toprowtext">{L_POSTS}</span></td>
	  <td class="toprow"><span class="toprowtext">{L_FROM}</span></td>
	  <td class="toprow"><span class="toprowtext">{L_EMAIL}</span></td>
	  <td class="toprow"><span class="toprowtext">{L_WEBSITE}</span></td>
	  <td class="toprow"><span class="toprowtext">{L_SELECT}</span></td>
	</tr>

	<tr> 
	  <td class="catrow" colspan="8"><span class="catrowtext">{L_GROUP_MODERATOR}</span></td>
	</tr>

	<tr> 
	  <td class="row1" align="center"> {MOD_PM_IMG} </td>
	  <td class="row1" align="center"><span class="mediumtext"><a href="{U_MOD_VIEWPROFILE}" class="mediumlink">{MOD_USERNAME}</a></span></td>
	  <td class="row1" align="center" valign="middle"><span class="mediumtext">{MOD_POSTS}</span></td>
	  <td class="row1" align="center" valign="middle"><span class="mediumtext">{MOD_FROM}</span></td>
	  <td class="row1" align="center" valign="middle"><span class="mediumtext">{MOD_EMAIL_IMG}</span></td>
	  <td class="row1" align="center">{MOD_WWW_IMG}</td>
	  <td class="row1" align="center">&nbsp;  </td>
	</tr>

	<tr> 
	  <td class="catrow" colspan="8"><span class="catrowtext">{L_GROUP_MEMBERS}</span></td>
	</tr>

	<!-- BEGIN member_row -->
	<tr> 
	  <td class="row1" align="center"> {member_row.PM_IMG} </td>
	  <td class="row1" align="center"><span class="mediumtext"><a href="{member_row.U_VIEWPROFILE}" class="mediumlink">{member_row.USERNAME}</a></span></td>
	  <td class="row1" align="center"><span class="mediumtext">{member_row.POSTS}</span></td>
	  <td class="row1" align="center"><span class="mediumtext"> {member_row.FROM} </span></td>
	  <td class="row1" align="center" valign="middle"><span class="mediumtext">{member_row.EMAIL_IMG}</span></td>
	  <td class="row1" align="center"> {member_row.WWW_IMG}</td>
	  <td class="row1" align="center"> 
	  <!-- BEGIN switch_mod_option -->
	  <input type="checkbox" name="members[]" value="{member_row.USER_ID}" /> 
	  <!-- END switch_mod_option -->
	  </td>
	</tr>
	<!-- END member_row -->

	<!-- BEGIN switch_no_members -->
	<tr> 
	  <td class="row1" colspan="7" align="center"><span class="mediumtext">{L_NO_MEMBERS}</span></td>
	</tr>
	<!-- END switch_no_members -->

	<!-- BEGIN switch_hidden_group -->
	<tr> 
	  <td class="row1" colspan="7" align="center"><span class="mediumtext">{L_HIDDEN_MEMBERS}</span></td>
	</tr>
	<!-- END switch_hidden_group -->

	<!-- BEGIN switch_mod_option -->
	<tr>
		<td class="catrow" colspan="8" align="right"><span class="catrowtext">
			<input type="submit" name="remove" value="{L_REMOVE_SELECTED}" />
		</span></td>
	</tr>
	<!-- END switch_mod_option -->
</table>
</td>
</tr>
</table>

  <table width="98%" cellspacing="2" border="0" align="center" cellpadding="2">
    <tr>
		<td align="left" valign="top">
		<!-- BEGIN switch_mod_option -->
		<span class="mediumtext"><input type="text" name="username" maxlength="50" size="20" /> <input type="submit" name="add" value="{L_ADD_MEMBER}" /> <input type="submit" name="usersubmit" value="{L_FIND_USERNAME}" onClick="window.open('{U_SEARCH_USER}', '_phpbbsearch', 'HEIGHT=250,resizable=yes,WIDTH=400');return false;" /></span><br /><br />
		<!-- END switch_mod_option -->
		<span class="mediumtext">{PAGE_NUMBER}</span></td>
		<td align="right" valign="top"><span class="smalltext">{S_TIMEZONE}</span><br /><span class="nav">{PAGINATION}</span></td>
	</tr>
</table>

{PENDING_USER_BOX}

{S_HIDDEN_FIELDS}</form>

<table width="100%" cellspacing="2" border="0" align="center">
  <tr> 
	<td valign="top" align="right">{JUMPBOX}</td>
  </tr>
</table>
