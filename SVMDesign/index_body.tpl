<!-- DEBUG marker: index_body.tpl starts here -->  
<table width="98%" border="0" cellspacing="2" cellpadding="2" align="center">
  <tr> 
    <td align="left" width="50%" valign="middle">
      <!-- BEGIN switch_user_logged_in -->
	  <span class="smalltext">
      <a href="{U_SEARCH_NEW}" class="smalllink">{L_SEARCH_NEW}</a><br>
	  </span>
      <!-- END switch_user_logged_in -->
      </td>
    <td align="right" width="50%" valign="middle">
      {CURRENT_TIME}<br>
      <!-- BEGIN switch_user_logged_in -->
      {LAST_VISIT_DATE} 
      <!-- END switch_user_logged_in -->

    </td>
  </tr>
</table>
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder"> 
      <table cellpadding="2" cellspacing="1" border="0" width="100%">
        <tr align="center"> 
          <td class="toprow" colspan="2"><b><span class="toprowtext">&nbsp;{L_FORUM}&nbsp;</span></b></td>
          <td class="toprow"><b><span class="toprowtext">&nbsp;{L_POSTS}&nbsp;</span></b></td>
          <td class="toprow"><b><span class="toprowtext">Threads</span></b></td>
          <td nowrap class="toprow"><b><span class="toprowtext">&nbsp;{L_LASTPOST}&nbsp;</span></b></td>
          <td width="20%" class="toprow"><b><span class="toprowtext">&nbsp;Moderator&nbsp;</span></b></td>
        </tr>
        <!-- BEGIN catrow -->
        <tr> 
          <td colspan="6" class="catrow">
			<span class="catrowtext">{catrow.CAT_DESC}</span>
          </td>
        </tr>
        <!-- BEGIN forumrow -->
        <tr align="center"> 
          <td valign="middle" class="row1" align="center"><img src="{catrow.forumrow.FORUM_FOLDER_IMG}" alt="{catrow.forumrow.L_FORUM_FOLDER_ALT}" title="{catrow.forumrow.L_FORUM_FOLDER_ALT}" /></td>
          <td align="left" class="row1" width="80%"><a href="{catrow.forumrow.U_VIEWFORUM}" class="forumlink">{catrow.forumrow.FORUM_NAME}</a><br>
            <span class="smalltext"> {catrow.forumrow.FORUM_DESC}<br>
            </span></td>
          <td class="row1"><span class="smalltext"><font size="2">{catrow.forumrow.POSTS}</font></span></td>
          <td class="row1"><span class="smalltext"><font size="2">{catrow.forumrow.TOPICS}</font></span></td>
          <td class="row1" align="right" nowrap> 
            <table width="100%">
              <tr> 
                <td nowrap align="right">{catrow.forumrow.LAST_POST}</td>
              </tr>
            </table>
          </td>
          <td class="row1" nowrap><span class="smalltext">{catrow.forumrow.MODERATORS}</span></td>
        </tr>
        <!-- END forumrow -->
        <!-- END catrow -->
        <tr> 
          <td colspan="6" class="catrow">
		    <span class="catrowtext">Miscellaneous</span>
		  </td>
        </tr>
        <tr> 

          <td valign="middle" class="row1" align="center"><img src="templates/SVMDesign/images/folder_new.gif" alt="{catrow.forumrow.L_FORUM_FOLDER_ALT}" title="{catrow.forumrow.L_FORUM_FOLDER_ALT}" /></td>

		  
	 <td colspan="3" class="row1">

	<!-- BEGIN switch_user_logged_in -->
	    <a href="{U_SEARCH_SELF}" class="mainmenu">{L_SEARCH_SELF}</a><br>
	<!-- END switch_user_logged_in -->

	    <a href="viewonline.php" class="mainmenu">View users currently online</a><b>&nbsp;</b><br>
	    <a href="archives.php" class="mainmenu">View archived SourceForge forums</a><b>&nbsp;[READ ONLY]</b>
	</td>		  

        <td colspan="2" class="row1" style="vertical-align: top;"><span class="smalltext"> 
		{TOTAL_POSTS}<br>
		{TOTAL_USERS}</span>
	</td>

	</tr>

      </table>
    </td>
  </tr>
</table>
<table width="98%" cellspacing="0" border="0" align="center" cellpadding="2">
  <tr> 
    <td align="left"><a href="{U_MARK_READ}" class="smalllink">{L_MARK_FORUMS_READ}</a></td>
    <td align="right" width="50%"><span class="smalltext">{S_TIMEZONE}</span></td>
  </tr>
</table>
<table width="98%" border="0" cellspacing="0" cellpadding="0" align="center">
  <tr> 
    <td align="center" width="100%"> 
      <table cellspacing="3" border="0" align="center" cellpadding="0">
        <tr> 
          <td width="20" align="center"><img src="templates/SVMDesign/images/folder_new.gif" alt="{L_NEW_POSTS}"/></td>
          <td><span class="smalltext">{L_NEW_POSTS}</span></td>
          <td>&nbsp;&nbsp;</td>
          <td width="20" align="center"><img src="templates/SVMDesign/images/folder.gif" alt="{L_NO_NEW_POSTS}" /></td>
          <td><span class="smalltext">{L_NO_NEW_POSTS}</span></td>
          <td>&nbsp;&nbsp;</td>
          <td width="20" align="center"><img src="templates/SVMDesign/images/folder_lock.gif" alt="{L_FORUM_LOCKED}" /></td>
          <td><span class="smalltext">A Closed Forum</span></td>
        </tr>
      </table>
    </td>
    <td align="right"> 
      <!-- BEGIN switch_user_logged_out -->
      <form method="post" action="{S_LOGIN_ACTION}">
        <table border="0" cellpadding="2" cellspacing="0">
          <tr> 
            <td nowrap><span class="smalltext">Login with username and password:</span></td>
          </tr>
          <tr> 
            <td nowrap align="center"> 
              <input class="post" type="text" name="username" size="10" />
              <input class="post" type="password" name="password" size="10" />
              <b>Auto Login?</b> 
              <input class="text" type="checkbox" name="autologin" value="ON" />
              <input type="submit" class="mainoption" name="login" value="{L_LOGIN}" />
              <br>
            </td>
          </tr>
        </table>
      </form>
      <!-- END switch_user_logged_out -->
    </td>
  </tr>
</table>
