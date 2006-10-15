<!-- DEBUG marker: viewforum_body.tpl starts here --> 
<form method="post" action="{S_POST_DAYS_ACTION}">
  <table cellpadding="2" cellspacing="0" border="0" width="98%"  align="center">
    <tr>
      <td style="vertical-align: middle;">	  
	    <img src="templates/SVMDesign/images/folder_new.gif" border="0" alt="Folder">
	  </td>
	  
      <td style="vertical-align: middle;" width="100%"><span 
      class="largetext"><a href="{U_INDEX}" class="largelink"><b>Forum Index</b></a>&nbsp;&gt;&nbsp;<a
      class="largelink" href="{U_VIEW_FORUM}"><b>{FORUM_NAME}</b></a></span></td>

	  <td style="vertical-align: middle;" align="right"><a href="{U_POST_NEW_TOPIC}"><img src="{POST_IMG}" border="0" alt="{L_POST_NEW_TOPIC}" /></a>
	  </td>

	  </tr>
	  <tr>
		<td colspan="2">
        (Moderated by:<b><span class="smalltext"> {MODERATORS}</span></b>)<br>
        <b><span class="smalltext">{PAGINATION} </span></b><br><span class="smalltext"><b>{LOGGED_IN_USER_LIST}</b></span>
		</td>

		<td align="right" style="white-space: nowrap;">
        <span class="smalltext"><a href="{U_MARK_READ}">{L_MARK_TOPICS_READ}
        </a><br>{S_WATCH_FORUM}</span>
      </td>
    </tr>
  </table>
  <table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
    <tr> 
      <td class="tableborder"> 
        <table cellpadding="4" cellspacing="1" border="0"  width="100%">
          <tr align="center"> 
            <td align="center" nowrap colspan="2" class="toprow" valign="middle">Thread</td>
            <td nowrap class="toprow" valign="middle"><span class="toprowtext">&nbsp;Thread 
              Starter&nbsp;</span></td>
            <td nowrap class="toprow" valign="middle"><span class="toprowtext">&nbsp;{L_REPLIES}&nbsp;</span></td>
            <td nowrap class="toprow" valign="middle"><span class="toprowtext">&nbsp;{L_VIEWS}&nbsp;</span></td>
            <td nowrap class="toprow" valign="middle"><span class="toprowtext">&nbsp;{L_LASTPOST}&nbsp;</span></td>
          </tr>
          <!-- BEGIN topicrow -->
          <tr align="center"> 
            <td class="row1" valign="middle"><img src="{topicrow.TOPIC_FOLDER_IMG}" alt="{topicrow.L_TOPIC_FOLDER_ALT}" title="{topicrow.L_TOPIC_FOLDER_ALT}" /></td>
            <td align="left" class="row1" width="100%"><span class="smalltext">{topicrow.NEWEST_POST_IMG}{topicrow.TOPIC_TYPE}<a href="{topicrow.U_VIEW_TOPIC}" class="topiclink">{topicrow.TOPIC_TITLE}</a></span><span class="smalltext"><br />
              {topicrow.GOTO_PAGE}</span></td>
            <td nowrap class="row1"><span class="smalltext">{topicrow.TOPIC_AUTHOR}</span></td>
            <td class="row1" nowrap><span class="mediumtext">{topicrow.REPLIES}</span></td>
            <td class="row1" nowrap><span class="mediumtext">{topicrow.VIEWS}</span></td>
            <td class="row1" align="right" nowrap><span class="smalltext">{topicrow.LAST_POST_TIME}<br />{topicrow.LAST_POST_AUTHOR} {topicrow.LAST_POST_IMG}</span></td>
          </tr>
          <!-- END topicrow -->
          <!-- BEGIN switch_no_topics -->
          <tr align="center"> 
            <td colspan="6" class="row1">Crap! Post some topics 
              already and let the discussion begin!</td>
          </tr>
          <!-- END switch_no_topics -->
          <tr> 
            <td width="100%" colspan="6" align="center" class="catrow">              
              <table width="100%" border="0" cellpadding="2" cellspacing="1">
                      <tr>
                        <td align="left" width="98%">
                          <table border="0" cellspacing="0" cellpadding="0">
                            <tr> 
                              <td valign="middle"><span class="largetext">&nbsp;&nbsp;{L_DISPLAY_TOPICS}:</span></td>
                              <td valign="middle"><span class="largetext">&nbsp;&nbsp;{S_SELECT_TOPIC_DAYS}</span></td>
                              <td align="left" valign="middle"><span class="largetext"> 
                                &nbsp;<input type="submit" value="{L_GO}" class="liteoption" name="submit" />
                                </span></td>
                            </tr>
                          </table>
			
                        </td>  
                       <td align="right" width="2%" nowrap><a href="{U_POST_NEW_TOPIC}"><img src="{POST_IMG}" border="0" alt="{L_POST_NEW_TOPIC}" /></a></td>                       
                      </tr>
               </table>              
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
  <table cellpadding="2" cellspacing="0" border="0" width="98%"  align="center">
    <tr valign="top"> 
      <td><span class="smalltext"><a href="{U_MARK_READ}">{L_MARK_TOPICS_READ}</a></span></td>
      <td align="right"><span class="smalltext">{PAGE_NUMBER}<br>
        </span><span class="nav">{PAGINATION}</span><span class="smalltext"><br>
        {S_TIMEZONE} </span></td>
    </tr>
  </table>
  </form>
  <table cellpadding="2" cellspacing="0" border="0" width="98%"  align="center">
  <tr> 
    <td colspan="2" align="center"><span class="smalltext">{S_TIMEZONE}. </span> 
      <span class="smalltext">{CURRENT_TIME}</span> </td>
  </tr>
  <tr> 
    <td rowspan="2">
      <table border="0" cellspacing="2" cellpadding="2" align="center" width="1%">
        <tr> 
          <td width="1%"><img src="templates/SVMDesign/images/folder_new.gif" alt="{L_NEW_POSTS}"></td>
		  <td nowrap style="text-align: left;">&nbsp;{L_NEW_POSTS}&nbsp;&nbsp;&nbsp;</td>
          <td width="1%"><img src="templates/SVMDesign/images/folder_new_hot.gif" alt="{L_NEW_POSTS_HOT}"></td>
		  <td nowrap style="text-align: left;">&nbsp;{L_NEW_POSTS_HOT}&nbsp;&nbsp;&nbsp;</td>
          <td width="1%"><img src="templates/SVMDesign/images/folder_lock.gif" alt="{L_NO_NEW_POSTS_TOPIC_LOCKED}"></td>
		  <td nowrap style="text-align: left;">&nbsp;Closed thread&nbsp;&nbsp;&nbsp;</td>
        </tr>
        <tr>
          <td width="1%"><img src="templates/SVMDesign/images/folder.gif" alt="{L_NO_NEW_POSTS}"></td>
		  <td nowrap style="text-align: left;">{L_NO_NEW_POSTS}&nbsp;&nbsp;&nbsp;</td>
          <td width="1%"><img src="templates/SVMDesign/images/folder_hot.gif" alt="{L_NO_NEW_POSTS_HOT}"></td>
		  <td nowrap style="text-align: left;" colspan="3">{L_NO_NEW_POSTS_HOT}&nbsp;&nbsp;&nbsp;</td>
        </tr>
      </table>
    </td>
  </tr>
</table>
<table cellpadding="2" cellspacing="0" border="0" width="98%"  align="center">
  <tr valign="bottom"> 
    <td align="left"><span class="smalltext"><b>Forum Rules:<br>
      </b></span> 
      <table cellpadding="0" cellspacing="0" border="0" align="left">
        <tr> 
          <td class="tableborder"> 
            <table cellpadding="4" cellspacing="1" border="0" align="left">
              <tr> 
                <td class="row1"><span class="smalltext" style="white-space: nowrap;">{S_AUTH_LIST}</span> 
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
    <td align="right">&nbsp;</td>
  </tr>
</table>
