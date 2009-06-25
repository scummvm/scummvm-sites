<!-- DEBUG: profile_send_email.tpl starts here -->

<script language="JavaScript" type="text/javascript">
<!--
function checkForm(formObj) {

	formErrors = false;    

	if (formObj.message.value.length < 2) {
		formErrors = "You must enter a message!";
	}
	else if ( formObj.subject.value.length < 2)
	{
		formErrors = "You must enter a subject!";
	}

	if (formErrors) {
		alert(formErrors);
		return false;
	}
}
//-->
</script>

<form action="{S_POST_ACTION}" method="post" name="post" onSubmit="return checkForm(this)">
  {ERROR_BOX} 
  <table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
  <table border="0" cellpadding="3" cellspacing="1" width="100%">
	      <tr align="center"> 
            <td class="catrow" colspan="2" height="25"><span class="catrowtext">{L_SEND_EMAIL_MSG}</span></td>
	</tr>
	<tr> 
		<td class="toprow" width="22%"><span class="toprowtext"><b>{L_RECIPIENT}</b></span></td>
		<td class="toprow" width="78%"><span class="toprowtext"><b>{USERNAME}</b></span> </td>
	</tr>
	<tr> 
		<td class="row1" width="22%"><span class="mediumtext"><b>{L_SUBJECT}</b></span></td>
		<td class="row1" width="78%"><span class="mediumtext"><input type="text" name="subject" size="45" maxlength="100" style="width:450px" tabindex="2" value="{SUBJECT}"></span> </td>
	</tr>
	<tr> 
		<td class="row1" valign="top"><span class="mediumtext"><b>{L_MESSAGE_BODY}</b></span><br><span class="smalltext">{L_MESSAGE_BODY_DESC}</span></td>
		<td class="row1"><span class="mediumtext"><textarea name="message" rows="25" cols="40" wrap="virtual" style="width:500px" tabindex="3">{MESSAGE}</textarea></span></td>
	</tr>
	<tr> 
		<td class="row1" valign="top"><span class="mediumtext"><b>{L_OPTIONS}</b></span></td>
		<td class="row1"><table cellspacing="0" cellpadding="1" border="0">
			<tr> 
				<td><input type="checkbox" name="cc_email"  value="1" checked></td>
				<td><span class="mediumtext">{L_CC_EMAIL}</span></td>
			</tr>
		</table></td>
	</tr>
	<tr>
		<td class="catBottom" colspan="2" align="center" height="28"> {S_HIDDEN_FORM_FIELDS} 
		&nbsp;<input type="submit" tabindex="6" name="submit" class="mainoption" value="{L_SEND_EMAIL}"></td>
	</tr>
</table>
</td>
</tr>
</table>
  <table width="98%" cellspacing="2" border="0" align="center" cellpadding="2">
    <tr> 
		<td align="right" valign="top"><span class="smalltext">{S_TIMEZONE}</span></td>
	</tr>
</table></form>

<table width="98%" cellspacing="2" border="0" align="center">
  <tr>
		<td valign="top" align="right">{JUMPBOX}</td>
	</tr>
</table>
