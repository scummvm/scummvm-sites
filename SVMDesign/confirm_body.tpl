<!-- DEBUG: confirm_body.tpl starts here-->
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
<table width="100%" border="0" cellspacing="1" cellpadding="3" class="forumline">
  <tr> 
	<td class="catrow" valign="middle" height="25" align="center"><span class="catrowtext">{MESSAGE_TITLE}</span></td>
  </tr>
  <tr> 
	<td class="row1" align="center"> 
	  <form action="{S_CONFIRM_ACTION}" method="POST">
		<span class="mediumtext"><br />
		{MESSAGE_TEXT}<br />
		<br />
		{S_HIDDEN_FIELDS} 
		<input type="submit" name="confirm" value="{L_YES}" />
		&nbsp;&nbsp; 
		<input type="submit" name="cancel" value="{L_NO}" />
		</span> 
	  </form>
	</td>
  </tr>
</table>
</td>
</tr>
</table>
<br />
