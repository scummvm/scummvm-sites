<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<!-- DEBUG marker: install.tpl starts here -->  

<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<meta http-equiv="Content-Style-Type" content="text/css">
<title>{L_INSTALLATION}</title>
<link rel="stylesheet" href="templates/SVMDesign/SVMDesign.css" type="text/css">
<style type="text/css">
<!--
@import url("templates/subSilver/formIE.css"); 
-->
</style>
</head>
<body bgcolor="#FFFFFF">
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
<table width="100%" border="0" cellspacing="0" cellpadding="0">
					<tr>
						<td><img src="templates/subSilver/images/logo_phpBB.gif" border="0" alt="Forum Home" vspace="1"></td>
						<td align="center" width="100%" valign="middle"><span class="maintitle">{L_INSTALLATION}</span></td>
					</tr>
				</table></td></tr></table>
<br>
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
      <table width="100%" border="0" align="center" cellspacing="0" cellpadding="0">
        <tr>
						<td><span class="mediumtext">{L_INSTRUCTION_TEXT}</span></td>
					</tr>
				</table>
				</td></tr></table>
<form action="{S_FORM_ACTION}" name="install_form" method="post">
 <table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
  <table width="100%" cellpadding="4" cellspacing="1" border="0">
    <!-- BEGIN switch_stage_one_install -->
          <tr align="center"> 
            <td colspan="2" class="catrow"><span class="catrowtext">{L_INITIAL_CONFIGURATION}</span></td>
					</tr>
					<tr>
						<td class="row1" align="right" width="30%"><span class="mediumtext">{L_LANGUAGE}: </span></td>
						<td class="row1">{S_LANG_SELECT}</td>
					</tr>
					<tr>
						<td class="row1" align="right"><span class="mediumtext">{L_DBMS}: </span></td>
						<td class="row1">{S_DBMS_SELECT}</td>
					</tr>
					<tr>
						<td class="row1" align="right"><span class="mediumtext">{L_UPGRADE}:</span></td>
						<td class="row1">{S_UPGRADE_SELECT}</td>
					</tr>
					
          <tr align="center"> 
            <td colspan="2" class="catrow"><span class="catrowtext">{L_DATABASE_CONFIGURATION}</span></td>
					</tr>
					<tr>
						<td class="row1" align="right"><span class="mediumtext">{L_DB_HOST}: </span></td>
						<td class="row1"><input type="text" name="dbhost" value="{DB_HOST}"></td>
					</tr>
					<tr>
						<td class="row1" align="right"><span class="mediumtext">{L_DB_NAME}: </span></td>
						<td class="row1"><input type="text" name="dbname" value="{DB_NAME}"></td>
					</tr>
					<tr>
						<td class="row1" align="right"><span class="mediumtext">{L_DB_USER}: </span></td>
						<td class="row1"><input type="text" name="dbuser" value="{DB_USER}"></td>
					</tr>
					<tr>
						<td class="row1" align="right"><span class="mediumtext">{L_DB_PASSWORD}: </span></td>
						<td class="row1"><input type="password" name="dbpasswd"></td>
					</tr>
					<tr>
						<td class="row1" align="right"><span class="mediumtext">{L_DB_PREFIX}: </span></td>
						<td class="row1"><input type="text" name="prefix" value="{DB_PREFIX}"></td>
					</tr>
					
          <tr align="center"> 
            <td colspan="2" class="catrow"><span class="catrowtext">{L_ADMIN_CONFIGURATION}</span></td>
					</tr>
					<tr>
						<td class="row1" align="right"><span class="mediumtext">{L_ADMIN_USERNAME}: </span></td>
						<td class="row1"><input type="text" name="admin_name" value="{ADMIN_USERNAME}"></td>
					</tr>
					<tr>
						<td class="row1" align="right"><span class="mediumtext">{L_ADMIN_PASSWORD}: </span></td>
						<td class="row1"><input type="password" name="admin_pass1"></td>
					</tr>
					<tr>
						<td class="row1" align="right"><span class="mediumtext">{L_ADMIN_CONFIRM_PASSWORD}: </span></td>
						<td class="row1"><input type="password" name="admin_pass2"></td>
					</tr>
					<!-- END switch_stage_one_install -->
					<!-- BEGIN switch_error_install -->
					<tr>
						
            <td class="catrow" align="center"><span class="catrowtext">{L_ERROR_TITLE}</span></td>
					</tr>
					<tr>
						<td class="row1" align="center"><span class="mediumtext">{L_ERROR}</span></td>
					</tr>
					<!-- END switch_error_install -->
					<!-- BEGIN switch_ftp_file -->
					
          <tr align="center"> 
            <td colspan="2" class="catrow"><span class="catrowtext">{L_FTP_INFO}</span></td>
					</tr>
					<tr>
						<td class="row1" align="right"><span class="mediumtext">{L_FTP_PATH}</span></td>
						<td class="row1"><input type="text" name="ftp_dir"></td>
					</tr>
					<tr>
						<td class="row1" align="right"><span class="mediumtext">{L_FTP_USER}</span></td>
						<td class="row1"><input type="text" name="ftp_user"></td>
					</tr>
					<tr>
						<td class="row1" align="right"><span class="mediumtext">{L_FTP_PASS}</span></td>
						<td class="row1"><input type="password" name="ftp_pass"></td>
					</tr>
					<!-- END switch_ftp_file -->
					<!-- BEGIN switch_ftp_option -->
					
          <tr align="center"> 
            <td colspan="2" class="catrow"><span class="catrowtext">{L_CHOOSE_FTP}</span></td>
					</tr>
					<tr>
						<td class="row1" align="right" width="50%"><span class="mediumtext">{L_ATTEMPT_FTP}</span></td>
						<td class="row1"><input type="radio" name="send_file" value="2"></td>
					</tr>
					<tr>
						<td class="row1" align="right" width="50%"><span class="mediumtext">{L_SEND_FILE}</span></td>
						<td class="row1"><input type="radio" name="send_file" value="1"></td>
					</tr>
					<!-- END switch_ftp_option -->
					<!-- BEGIN switch_common_install -->
					<tr> 
					  <td class="catrow" align="center" colspan="2">{S_HIDDEN_FIELDS}<input type="submit" value="{L_SUBMIT}"></td>
					</tr>
					<!-- END switch_common_install -->
					<!-- BEGIN switch_upgrade_install -->
					<tr>
						<td class="catrow" align="center" colspan="2"><span class="catrowtext">{L_UPGRADE_INST}</span></td>
					</tr>
					<tr>
						<td class="catrow" align="center" colspan="2"><input type="submit" name="upgrade_now" value="{L_UPGRADE_SUBMIT}">
						</td>
					</tr></table></td></tr></table>
</form>
					<!-- END switch_upgrade_install -->
				
</body>
</html>
