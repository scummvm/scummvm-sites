<!-- groupcp_pending_info.tpl -->
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
      <table width="100%" cellpadding="4" cellspacing="1" border="0">
        <tr align="center" valign="middle"> 
          <td class="toprow"><span class="toprowtext">{L_PM}</span></td>
	      <td class="toprow"><span class="toprowtext">{L_USERNAME}</span></td>
	      <td class="toprow"><span class="toprowtext">{L_POSTS}</span></td>
	      <td class="toprow"><span class="toprowtext">{L_FROM}</span></td>
	      <td class="toprow"><span class="toprowtext">{L_EMAIL}</span></td>
	      <td class="toprow"><span class="toprowtext">{L_WEBSITE}</span></td>
	      <td class="toprow"><span class="toprowtext">{L_SELECT}</span></td>
	</tr>
	<tr> 
	  <td class="catrow" colspan="8"><span class="catrowtext">{L_PENDING_MEMBERS}</span></td>
	</tr>
	<!-- BEGIN pending_members_row -->
	<tr> 
	  <td class="row1" align="center"> {pending_members_row.PM_IMG} /td>
	  <td class="row1" align="center"><span class="mediumtext"><a href="{pending_members_row.U_VIEWPROFILE}" class="mediumlink">{pending_members_row.USERNAME}</a></span></td>
	  <td class="row1" align="center"><span class="mediumtext">{pending_members_row.POSTS}</span></td>
	  <td class="row1" align="center"><span class="mediumtext">{pending_members_row.FROM}</span></td>
	  <td class="row1" align="center"><span class="mediumtext">{pending_members_row.EMAIL_IMG}</span></td>
	  <td class="row1" align="center"><span class="mediumtext">{pending_members_row.WWW_IMG}</span></td>
	  <td class="row1" align="center"><span class="smalltext"> <input type="checkbox" name="pending_members[]" value="{pending_members_row.USER_ID}" /></span></td>
	</tr>
	<!-- END pending_members_row -->
	<tr> 
	  <td class="catrow" colspan="8" align="right"><span class="catrowtext"> 
		<input type="submit" name="approve" value="{L_APPROVE_SELECTED}" />
		&nbsp; 
		<input type="submit" name="deny" value="{L_DENY_SELECTED}" />
		</span></td>
	</tr>
</table>
</td>
</tr>
</table>
