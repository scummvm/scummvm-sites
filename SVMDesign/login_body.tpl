<!-- DEBUG marker: login_body starts here -->  
<form action="{S_LOGIN_ACTION}" method="post">
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
  <table width="100%" cellpadding="4" cellspacing="1" border="0" align="center">
  <tr> 
	  <td class="toprow" align="center"><span class="toprowtext">{L_ENTER_PASSWORD}</span></td>
  </tr>
  <tr> 
	<td class="row1"><table border="0" cellpadding="3" cellspacing="1" width="100%">
		  <tr> 
			<td colspan="2" align="center">&nbsp;</td>
		  </tr>
		  <tr> 
			<td width="45%" align="right"><span class="mediumtext">{L_USERNAME}:</span></td>
			<td> 
			  <input type="text" name="username" size="25" maxlength="40" value="{USERNAME}" />
			</td>
		  </tr>
		  <tr> 
			<td align="right"><span class="mediumtext">{L_PASSWORD}:</span></td>
			<td> 
			  <input type="password" name="password" size="25" maxlength="100" />
			</td>
		  </tr>
		  <tr align="center"> 
			<td colspan="2"><span class="mediumtext">{L_AUTO_LOGIN}: <input type="checkbox" name="autologin" /></span></td>
		  </tr>
		  <tr align="center"> 
			<td colspan="2">{S_HIDDEN_FIELDS}<input type="submit" name="login" class="mainoption" value="{L_LOGIN}" /></td>
		  </tr>
		  <tr align="center"> 
			<td colspan="2"><span class="smalltext"><a href="{U_SEND_PASSWORD}" class="smalllink">{L_SEND_PASSWORD}</a></span></td>
		  </tr>
		</table></td>
  </tr>
</table>
</td>
</tr>
</table>
</form>
