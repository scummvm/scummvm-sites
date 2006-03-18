<!-- groupcp_user_body.tpl -->
<!--
 <table cellpadding="2" cellspacing="0" border="0" width="98%"  align="center">
  <tr> 
	  <td><img src="templates/SVMDesign/images/folder_new.gif" border="0" alt="Folder"></td>
      <td style="vertical-align: middle;" width="100%"><span 
      class="largetext"><a href="{U_INDEX}" class="largelink"><b>Forum Index</b></a></span></td>
  </tr>
</table>
-->
 <table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
<table width="100%" cellpadding="4" cellspacing="1" border="0">
  <!-- BEGIN switch_groups_joined -->
  <tr> 
	<!-- debug: A -->
	<td colspan="2" align="center" class="toprow"><span class="toprowtext">{L_GROUP_MEMBERSHIP_DETAILS}</span></td>
  </tr>
  <!-- BEGIN switch_groups_member -->
  <tr> 
    <!-- debug: B -->
	<td colspan="2" class="row1">
	  <form method="get" action="{S_USERGROUP_ACTION}">
	  <table cellspacing="0" cellpadding="0" border="0" width="100%">
	  <tr>
		<td width="33%" class="row1"><span class="mediumtext">{L_YOU_BELONG_GROUPS}</span></td>
		<td width="33%" align="center"><span class="smalltext">{GROUP_MEMBER_SELECT}</span></td>
		<td align="center" width="33%"> 
			  <input type="submit" value="{L_VIEW_INFORMATION}" />{S_HIDDEN_FIELDS}
			</td>
		</tr>
	  </table>
	  </form>
	</td>
		
  </tr>
  <!-- END switch_groups_member -->
  <!-- BEGIN switch_groups_pending -->
  
  <tr> 
  	<td colspan="2" class="row1">
		<form method="get" action="{S_USERGROUP_ACTION}">
		<table cellspacing="0" cellpadding="0" border="0" width="100%">
		<tr>
			<td class="row1" width="33%"><span class="mediumtext">{L_PENDING_GROUPS}</span></td>
			<td class="row1" width="33%" align="center">
				<span class="smalltext">{GROUP_PENDING_SELECT}</span></td>
			<td align="center" width="33%"> 
			  <input type="submit" value="{L_VIEW_INFORMATION}" />{S_HIDDEN_FIELDS}
			</td>
		</tr>
	  </table>
	  </form>
	</td>
  </tr>
  
  <!-- END switch_groups_pending -->
  <!-- END switch_groups_joined -->
  <!-- BEGIN switch_groups_remaining -->
  <tr> 
    <!-- debug: D -->
	<td colspan="2" align="center" class="toprow"><span class="toprowtext">{L_JOIN_A_GROUP}</span></td>
  </tr>
  <tr> 
	<td colspan="2" class="row1">
	  <form method="get" action="{S_USERGROUP_ACTION}">
	  <table cellspacing="0" cellpadding="0" border="0" width="100%">
	  <tr>
		<td width="33%"><span class="mediumtext">{L_SELECT_A_GROUP}</span></td>
		<td width="33%" class="row1" align="center"><span class="smalltext">{GROUP_LIST_SELECT}</span></td>
		<td width="33%" class="row1" align="center">
		  <input type="submit" value="{L_VIEW_INFORMATION}" />{S_HIDDEN_FIELDS}
		</td>
	  </tr>
	  </table>
	  </form>
	</td>
  </tr>
  <!-- END switch_groups_remaining -->
</table>
</td>
</tr>
</table>

<table width="98%" cellspacing="2" border="0" align="center" cellpadding="2">
  <tr> 
	<td align="right" valign="top"><span class="gensmall">{S_TIMEZONE}</span></td>
  </tr>
</table>

<br clear="all" />

<table width="98%" cellspacing="2" border="0" align="center">
  <tr> 
	<td valign="top" align="right">{JUMPBOX}</td>
  </tr>
</table>
