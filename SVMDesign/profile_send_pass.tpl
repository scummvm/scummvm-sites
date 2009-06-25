<!-- DEBUG: profile_send_pass.tpl starts here -->
<form action="{S_PROFILE_ACTION}" method="post">
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
  <table border="0" cellpadding="3" cellspacing="1" width="100%">
	      <tr align="center"> 
            <td class="toprow" colspan="2" valign="middle"><span class="toprowtext">{L_SEND_PASSWORD}</span></td>
	</tr>
	<tr> 
	  <td class="row1" colspan="2"><span class="smalltext">{L_ITEMS_REQUIRED}</span></td>
	</tr>
	<tr> 
	  <td class="row1" width="38%"><span class="mediumtext">{L_USERNAME}: *</span></td>
	  <td class="row1"> 
		<input type="text" style="width: 200px" name="username" size="25" maxlength="40" value="{USERNAME}">
	  </td>
	</tr>
	<tr> 
	  <td class="row1"><span class="mediumtext">{L_EMAIL_ADDRESS}: *</span></td>
	  <td class="row1"> 
		<input type="text" class="post" style="width: 200px" name="email" size="25" maxlength="255" value="{EMAIL}">
	  </td>
	</tr>
	<tr> 
	        <td class="catrow" colspan="2" align="center">{S_HIDDEN_FIELDS} 
              <input type="submit" name="submit" value="{L_SUBMIT}">
		&nbsp;&nbsp; 
		<input type="reset" value="{L_RESET}" name="reset">
	  </td>
	</tr>
  </table>
  </td>
  </tr>
  </table>
</form>
