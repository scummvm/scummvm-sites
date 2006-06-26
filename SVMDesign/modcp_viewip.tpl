<!-- DEBUG: modcp_viewip.tpl starts here --> 
 <table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
<table width="100%" cellpadding="4" cellspacing="1" border="0" class="forumline">
  <tr> 
	<td class="toprow"><span class="toprowtext">{L_IP_INFO}</span></td>
  </tr>
  <tr> 
	<td class="catrow"><span class="catrowtext">{L_THIS_POST_IP}</span></td>
  </tr>
  <tr> 
	<td class="row1"> 
	  <table width="100%" cellspacing="0" cellpadding="0" border="0">
		<tr> 
		  <td>&nbsp;<span class="smalltext">{IP}</span></td>
		  <td align="right"><span class="smalltext">[ <a href="{U_LOOKUP_IP}" class="smalllink">{L_LOOKUP_IP}</a> ]&nbsp;</span></td>
		</tr>
	  </table>
	</td>
  </tr>
  <tr> 
	<td class="catrow"><span class="catrowtext">{L_OTHER_USERS}</span></td>
  </tr>
  <!-- BEGIN userrow -->
  <tr> 
	<td class="row1"> 
	  <table width="100%" cellspacing="0" cellpadding="0" border="0">
		<tr> 
		  <td>&nbsp;<span class="smalltext"><a href="{userrow.U_PROFILE}" class="smalltext">{userrow.USERNAME}</a></span></td>
		  <td align="right"><a href="{userrow.U_SEARCHPOSTS}" class="smalltext"><img src="{SEARCH_IMG}" border="0" alt="{L_SEARCH_POSTS}" /></a> 
			&nbsp;</td>
		</tr>
	  </table>
	</td>
  </tr>
  <!-- END userrow -->
  <tr> 
	<td class="catrow"><span class="catrowtext">{L_OTHER_IPS}</span></td>
  </tr>
  <!-- BEGIN iprow -->
  <tr> 
	<td class="row1"><table width="100%" cellspacing="0" cellpadding="0" border="0">
		<tr> 
		  <td>&nbsp;<span class="smalltext">{iprow.IP}</span></td>
		  <td align="right"><span class="smalltext">[ <a href="{iprow.U_LOOKUP_IP}" class="smalltext">{L_LOOKUP_IP}</a> 
			]&nbsp;</span></td>
		</tr>
	  </table></td>
  </tr>
  <!-- END iprow -->
</table>
</td>
</tr>
</table>
<br clear="all" />
