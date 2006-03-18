<!-- DEBUG: profile_add_body.tpl starts here -->
<!--
<TABLE cellpadding="2" cellspacing="0" border="0" width="98%"  align="center">
  <TR> 
	  <td><img src="templates/SVMDesign/images/folder_new.gif" border="0" alt="Folder"></td>
      <td style="vertical-align: middle;" width="100%"><span 
      class="largetext"><a href="{U_INDEX}" class="largelink"><b>Forum Index</b></a></span></td>
  </TR>
</TABLE>
-->
<FORM action="{S_PROFILE_ACTION}" enctype="multipart/form-data" method="post">
  {ERROR_BOX} 
  <TABLE cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <TR> 
    <TD class="tableborder">
        <TABLE border="0" cellpadding="3" cellspacing="1" width="100%" class="forumline">
          <TR align="center"> 
            <TD class="toprow" colspan="2"  valign="middle"><SPAN class="toprowtext">{L_REGISTRATION_INFO}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1" colspan="2"><SPAN class="largetext">{L_ITEMS_REQUIRED}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1" width="38%"><B><SPAN class="largetext">{L_USERNAME}: 
              *</SPAN></B></TD>
            <TD class="row1"> 
              <INPUT type="text" class="post" style="width: 200px" name="username" size="25" maxlength="40" value="{USERNAME}" />
            </TD>
          </TR>
          <TR> 
            <TD class="row1"><B><SPAN class="largetext">{L_EMAIL_ADDRESS}: *</SPAN></B></TD>
            <TD class="row1"> 
              <INPUT type="text" class="post" style="width: 200px" name="email" size="25" maxlength="255" value="{EMAIL}" />
            </TD>
          </TR>
          <!-- BEGIN switch_edit_profile -->
          <TR> 
            <TD class="row1"><SPAN class="largetext"><B>{L_CURRENT_PASSWORD}: 
              *</B></SPAN><BR />
              <SPAN class="largetext">{L_PASSWORD_IF_CHANGED}</SPAN></TD>
            <TD class="row1"> 
              
							<INPUT type="password" class="post" style="width: 200px" name="cur_password" size="25" maxlength="100" value="{CUR_PASSWORD}" />
            </TD>
          </TR>
          <!-- END switch_edit_profile -->
          <TR> 
            <TD class="row1"><SPAN class="largetext"><B>{L_NEW_PASSWORD}: *</B></SPAN><BR />
              <SPAN class="largetext">{L_PASSWORD_IF_CHANGED}</SPAN></TD>
            <TD class="row1"> 
              
							<INPUT type="password" class="post" style="width: 200px" name="new_password" size="25" maxlength="100" value="{NEW_PASSWORD}" />
            </TD>
          </TR>
          <TR> 
            <TD class="row1"><SPAN class="largetext"><B>{L_CONFIRM_PASSWORD}: 
              * </B></SPAN><BR />
              <SPAN class="largetext">{L_PASSWORD_CONFIRM_IF_CHANGED}</SPAN></TD>
            <TD class="row1"> 
              <INPUT type="password" class="post" style="width: 200px" name="password_confirm" size="25" maxlength="100" value="{PASSWORD_CONFIRM}" />
            </TD>
          </TR>
<!-- BEGIN switch_confirm -->
<tr>
	<td class="row1" colspan="2" align="center">
{CONFIRM_IMG}<br />
<span class="smalltext">{L_CONFIRM_CODE_IMPAIRED}</span>
	</td>
</tr>
          <TR> 
            <TD class="row1"><SPAN class="largetext"><B>{L_CONFIRM_CODE}: * </B></TD>
            <TD class="row1"> 
<input type="text" class="post" style="width: 200px" name="confirm_code" size="6" maxlength="6" value="" /><br />
<span class="smalltext">{L_CONFIRM_CODE_EXPLAIN}</span>
            </TD>
          </TR>
<!-- END switch_confirm -->
          <TR align="center"> 
            <TD class="toprow" colspan="2" valign="middle"><SPAN class="toprowtext">{L_PROFILE_INFO}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1" colspan="2"><SPAN class="largetext">{L_PROFILE_INFO_NOTICE}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1"><B><SPAN class="largetext">{L_ICQ_NUMBER}:</SPAN></B></TD>
            <TD class="row1"> 
              <INPUT type="text" name="icq" class="post"style="width: 100px"  size="10" maxlength="15" value="{ICQ}" />
            </TD>
          </TR>
          <TR> 
            <TD class="row1"><B><SPAN class="largetext">{L_AIM}:</SPAN></B></TD>
            <TD class="row1"> 
              <INPUT type="text" class="post"style="width: 150px"  name="aim" size="20" maxlength="255" value="{AIM}" />
            </TD>
          </TR>
          <TR> 
            <TD class="row1"><B><SPAN class="largetext">{L_MESSENGER}:</SPAN></B></TD>
            <TD class="row1"> 
              <INPUT type="text" class="post"style="width: 150px"  name="msn" size="20" maxlength="255" value="{MSN}" />
            </TD>
          </TR>
          <TR> 
            <TD class="row1"><B><SPAN class="largetext">{L_YAHOO}:</SPAN></B></TD>
            <TD class="row1"> 
              <INPUT type="text" class="post"style="width: 150px"  name="yim" size="20" maxlength="255" value="{YIM}" />
            </TD>
          </TR>
          <TR> 
            <TD class="row1"><B><SPAN class="largetext">{L_WEBSITE}:</SPAN></B></TD>
            <TD class="row1"> 
              <INPUT type="text" class="post"style="width: 200px"  name="website" size="25" maxlength="255" value="{WEBSITE}" />
            </TD>
          </TR>
          <TR> 
            <TD class="row1"><B><SPAN class="largetext">{L_LOCATION}:</SPAN></B></TD>
            <TD class="row1"> 
              <INPUT type="text" class="post"style="width: 200px"  name="location" size="25" maxlength="100" value="{LOCATION}" />
            </TD>
          </TR>
          <TR> 
            <TD class="row1"><B><SPAN class="largetext">{L_OCCUPATION}:</SPAN></B></TD>
            <TD class="row1"> 
              <INPUT type="text" class="post"style="width: 200px"  name="occupation" size="25" maxlength="100" value="{OCCUPATION}" />
            </TD>
          </TR>
          <TR> 
            <TD class="row1"><B><SPAN class="largetext">{L_INTERESTS}:</SPAN></B></TD>
            <TD class="row1"> 
              <INPUT type="text" class="post"style="width: 200px"  name="interests" size="35" maxlength="150" value="{INTERESTS}" />
            </TD>
          </TR>
          <TR> 
            <TD class="row1"><SPAN class="largetext"><B>{L_SIGNATURE}:</B></SPAN><BR />
              <SPAN class="largetext">{L_SIGNATURE_EXPLAIN}<BR />
              <BR />
              {HTML_STATUS}<BR />
              {BBCODE_STATUS}<BR />
              {SMILIES_STATUS}</SPAN></TD>
            <TD class="row1"> 
              <TEXTAREA name="signature"style="width: 300px"  rows="6" cols="30" class="post">{SIGNATURE}</TEXTAREA>
            </TD>
          </TR>
          <TR align="center"> 
            <TD class="toprow" colspan="2"  valign="middle"><SPAN class="toprowtext">{L_PREFERENCES}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1"><B><SPAN class="largetext">{L_PUBLIC_VIEW_EMAIL}:</SPAN></B></TD>
            <TD class="row1"> 
              <INPUT type="radio" name="viewemail" value="1" {VIEW_EMAIL_YES} />
              <SPAN class="largetext">{L_YES}</SPAN>&nbsp;&nbsp; 
              <INPUT type="radio" name="viewemail" value="0" {VIEW_EMAIL_NO} />
              <SPAN class="largetext">{L_NO}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1"><B><SPAN class="largetext">{L_HIDE_USER}:</SPAN></B></TD>
            <TD class="row1"> 
              <INPUT type="radio" name="hideonline" value="1" {HIDE_USER_YES} />
              <SPAN class="largetext">{L_YES}</SPAN>&nbsp;&nbsp; 
              <INPUT type="radio" name="hideonline" value="0" {HIDE_USER_NO} />
              <SPAN class="largetext">{L_NO}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1"><SPAN class="largetext"><B>{L_NOTIFY_ON_REPLY}:</B></SPAN><BR />
              <SPAN class="largetext">{L_NOTIFY_ON_REPLY_EXPLAIN}</SPAN></TD>
            <TD class="row1"> 
              <INPUT type="radio" name="notifyreply" value="1" {NOTIFY_REPLY_YES} />
              <SPAN class="largetext">{L_YES}</SPAN>&nbsp;&nbsp; 
              <INPUT type="radio" name="notifyreply" value="0" {NOTIFY_REPLY_NO} />
              <SPAN class="largetext">{L_NO}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1"><SPAN class="largetext"><B>{L_NOTIFY_ON_PRIVMSG}:</B></SPAN></TD>
            <TD class="row1"> 
              <INPUT type="radio" name="notifypm" value="1" {NOTIFY_PM_YES} />
              <SPAN class="largetext">{L_YES}</SPAN>&nbsp;&nbsp; 
              <INPUT type="radio" name="notifypm" value="0" {NOTIFY_PM_NO} />
              <SPAN class="largetext">{L_NO}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1"><SPAN class="largetext"><B>{L_POPUP_ON_PRIVMSG}:</B></SPAN><BR />
              <SPAN class="largetext">{L_POPUP_ON_PRIVMSG_EXPLAIN}</SPAN></TD>
            <TD class="row1"> 
              <INPUT type="radio" name="popup_pm" value="1" {POPUP_PM_YES} />
              <SPAN class="largetext">{L_YES}</SPAN>&nbsp;&nbsp; 
              <INPUT type="radio" name="popup_pm" value="0" {POPUP_PM_NO} />
              <SPAN class="largetext">{L_NO}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1"><B><SPAN class="largetext">{L_ALWAYS_ADD_SIGNATURE}:</SPAN></B></TD>
            <TD class="row1"> 
              <INPUT type="radio" name="attachsig" value="1" {ALWAYS_ADD_SIGNATURE_YES} />
              <SPAN class="largetext">{L_YES}</SPAN>&nbsp;&nbsp; 
              <INPUT type="radio" name="attachsig" value="0" {ALWAYS_ADD_SIGNATURE_NO} />
              <SPAN class="largetext">{L_NO}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1"><B><SPAN class="largetext">{L_ALWAYS_ALLOW_BBCODE}:</SPAN></B></TD>
            <TD class="row1"> 
              <INPUT type="radio" name="allowbbcode" value="1" {ALWAYS_ALLOW_BBCODE_YES} />
              <SPAN class="largetext">{L_YES}</SPAN>&nbsp;&nbsp; 
              <INPUT type="radio" name="allowbbcode" value="0" {ALWAYS_ALLOW_BBCODE_NO} />
              <SPAN class="largetext">{L_NO}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1"><B><SPAN class="largetext">{L_ALWAYS_ALLOW_HTML}:</SPAN></B></TD>
            <TD class="row1"> 
              <INPUT type="radio" name="allowhtml" value="1" {ALWAYS_ALLOW_HTML_YES} />
              <SPAN class="largetext">{L_YES}</SPAN>&nbsp;&nbsp; 
              <INPUT type="radio" name="allowhtml" value="0" {ALWAYS_ALLOW_HTML_NO} />
              <SPAN class="largetext">{L_NO}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1"><B><SPAN class="largetext">{L_ALWAYS_ALLOW_SMILIES}:</SPAN></B></TD>
            <TD class="row1"> 
              <INPUT type="radio" name="allowsmilies" value="1" {ALWAYS_ALLOW_SMILIES_YES} />
              <SPAN class="largetext">{L_YES}</SPAN>&nbsp;&nbsp; 
              <INPUT type="radio" name="allowsmilies" value="0" {ALWAYS_ALLOW_SMILIES_NO} />
              <SPAN class="largetext">{L_NO}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1"><B><SPAN class="largetext">{L_BOARD_LANGUAGE}:</SPAN></B></TD>
            <TD class="row1"><SPAN class="largetext">{LANGUAGE_SELECT}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1"><SPAN class="largetext">{L_BOARD_STYLE}:</SPAN></TD>
            <TD class="row1"><SPAN class="largetext">{STYLE_SELECT}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1"><SPAN class="largetext"><B>{L_TIMEZONE}:</B></SPAN></TD>
            <TD class="row1"><SPAN class="largetext">{TIMEZONE_SELECT}</SPAN></TD>
          </TR>
          <TR> 
            <TD class="row1"><SPAN class="largetext"><B>{L_DATE_FORMAT}:</B></SPAN><BR />
              <SPAN class="largetext">{L_DATE_FORMAT_EXPLAIN}</SPAN></TD>
            <TD class="row1"> 
              <INPUT type="text" name="dateformat" value="{DATE_FORMAT}" maxlength="16" class="post" />
            </TD>
          </TR>
          <!-- BEGIN switch_avatar_block -->
          <TR> 
            <TD class="toprow" colspan="2" valign="middle" align="center">{L_AVATAR_PANEL}</TD>
          </TR>
          <TR> 
            <TD class="row1" colspan="2">
              <TABLE width="70%" cellspacing="2" cellpadding="0" border="0" align="center">
                <TR> 
                  <TD width="65%"><SPAN class="gensmall">{L_AVATAR_EXPLAIN}</SPAN></TD>
                  <TD align="center"><SPAN class="gensmall">{L_CURRENT_IMAGE}</SPAN><BR />
                    {AVATAR}<BR />
                    <INPUT type="checkbox" name="avatardel" />
                    &nbsp;<SPAN class="gensmall">{L_DELETE_AVATAR}</SPAN></TD>
                </TR>
              </TABLE>
            </TD>
          </TR>
          <!-- BEGIN switch_avatar_local_upload -->
          <TR> 
            <TD class="row1"><SPAN class="gen">{L_UPLOAD_AVATAR_FILE}:</SPAN></TD>
            <TD class="row1">
              <INPUT type="hidden" name="MAX_FILE_SIZE" value="{AVATAR_SIZE}" />
              <INPUT type="file" name="avatar" class="post" style="width:200px" />
            </TD>
          </TR>
          <!-- END switch_avatar_local_upload -->
          <!-- BEGIN switch_avatar_remote_upload -->
          <TR> 
            <TD class="row1"><SPAN class="gen">{L_UPLOAD_AVATAR_URL}:</SPAN><BR />
              <SPAN class="gensmall">{L_UPLOAD_AVATAR_URL_EXPLAIN}</SPAN></TD>
            <TD class="row1">
              <INPUT type="text" name="avatarurl" size="40" class="post" style="width:200px" />
            </TD>
          </TR>
          <!-- END switch_avatar_remote_upload -->
          <!-- BEGIN switch_avatar_remote_link -->
          <TR> 
            <TD class="row1"><SPAN class="gen">{L_LINK_REMOTE_AVATAR}:</SPAN><BR />
              <SPAN class="gensmall">{L_LINK_REMOTE_AVATAR_EXPLAIN}</SPAN></TD>
            <TD class="row1">
              <INPUT type="text" name="avatarremoteurl" size="40" class="post" style="width:200px" />
            </TD>
          </TR>
          <!-- END switch_avatar_remote_link -->
          <!-- BEGIN switch_avatar_local_gallery -->
          <TR> 
            <TD class="row1"><SPAN class="gen">{L_AVATAR_GALLERY}:</SPAN></TD>
            <TD class="row1">
              <INPUT type="submit" name="avatargallery" value="{L_SHOW_GALLERY}" class="liteoption" />
            </TD>
          </TR>
          <!-- END switch_avatar_local_gallery -->
          <!-- END switch_avatar_block -->
          <TR> 
            <TD class="catrow" colspan="2" align="center">{S_HIDDEN_FIELDS} 
              <INPUT type="submit" name="submit" value="{L_SUBMIT}" class="mainoption" />
              &nbsp;&nbsp; 
              <INPUT type="reset" value="{L_RESET}" name="reset" class="liteoption" />
            </TD>
          </TR>
        </TABLE>
  </TD>
  </TR>
  </TABLE>
</FORM>
