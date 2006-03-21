<!-- DEBUG: viewtopic_body.tpl -->
<script language="Javascript" type="text/javascript">
<!--
function create_icq_subsilver(icq_user_addr, icq_status_img, icq_add_img)
{
	if( icq_user_addr.length && icq_user_addr.indexOf("&nbsp;") == -1 )
	{
		document.write('<table width="59" border="0" cellspacing="0" cellpadding="0"><tr><td nowrap="nowrap" style=" background-image: url(\'' + icq_add_img + '\'); background-repeat: no-repeat"><img src="images/spacer.gif" width="3" height="18" alt = "">' + icq_status_img + '<a href="http://wwp.icq.com/scripts/search.dll?to=' + icq_user_addr + '"><img src="images/spacer.gif" width="35" height="18" border="0" alt="{L_ICQ_NUMBER}" /><\/a><\/td><\/tr><\/table><br>');
	}
}
//-->
</script>

<table cellpadding="2" cellspacing="0" border="0" width="98%"  align="center">
  <tr> 
	  <td><img src="templates/SVMDesign/images/folder_new.gif" border="0" alt="Folder"></td>
      <td style="vertical-align: middle;" width="100%"><span 
      class="largetext"><a href="{U_INDEX}" class="largelink"><b>Forum Index</b></a>&nbsp;&gt;&nbsp;<a
      class="largelink" href="{U_VIEW_FORUM}"><b>{FORUM_NAME}</b></a></span></td>
  </tr>
      
  <tr>
	<td colspan="2">
      <b><span class="smalltext">{PAGINATION}<br><br></span></b>
      </td>
  </tr>
</table>
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">

  <tr>
	<td class="toprow" nowrap ><span class="toprowtext">{TOPIC_TITLE}</span></td>
  </tr>
  
  
  <tr> 
    <td class="tableborder">
      <table border="0" cellpadding="0" cellspacing="0" width="100%">
        {POLL_DISPLAY} 
        <tr> 
          <td class="catrow" nowrap >
            <table width="100%" border="0" cellspacing="0" cellpadding="2">
              <tr> 
                <td width="186"><span class="largetext">&nbsp;&nbsp;{L_AUTHOR} 
                  </span></td>
                <td><span class="largetext">&nbsp;&nbsp;&nbsp;Thread</span></td>
                <td align="right"><!--<a href="{U_POST_NEW_TOPIC}"><img src="{POST_IMG}" border="0" alt="{L_POST_NEW_TOPIC}" align="middle" /></a>&nbsp;&nbsp;&nbsp;--><a href="{U_POST_REPLY_TOPIC}"><img src="{REPLY_IMG}" border="0" alt="{L_POST_REPLY_TOPIC}" align="middle" /></a></td>
              </tr>
            </table>
          </td>
        </tr>
        <!-- BEGIN postrow -->
        <tr align="center"> 
          <td class="tableborder">
            <table width="100%" border="0" cellspacing="1" cellpadding="4">
              <tr> 
                <td width="186" valign="top" class="row3" nowrap> <span class="largetext"><a name="{postrow.U_POST_ID}"></a><b>{postrow.POSTER_NAME}</b></span><br />
                  <span class="smalltext">{postrow.POSTER_RANK}<br />
                  {postrow.RANK_IMAGE}{postrow.POSTER_AVATAR}<br />
                  <br />
                  {postrow.POSTER_JOINED}<br />
                  {postrow.POSTER_POSTS}<br />
                  {postrow.POSTER_FROM}</span></td>
                <td valign="top" class="row3"> <span class="smalltext"><b>{postrow.POST_SUBJECT}</b></span> 
                  <p><span class="largetext">{postrow.MESSAGE}{postrow.SIGNATURE}</span><span class="smalltext">{postrow.EDITED_MESSAGE}<br></span>
                  <div align="right"> {postrow.EDIT_IMG}&nbsp;{postrow.QUOTE_IMG}&nbsp;{postrow.DELETE_IMG}&nbsp;{postrow.IP_IMG}</div>
                </td>
              </tr>
              <tr> 
                <td width="186" height="16" nowrap class="row1"><a href="{postrow.U_MINI_POST}"><img src="{postrow.MINI_POST_IMG}" alt="{postrow.L_MINI_POST_ALT}" title="{postrow.L_MINI_POST_ALT}" border="0" /></a><span class="smalltext"> 
                  {postrow.POST_DATE}<span class="mediumtext">&nbsp;</span></span></td>
                <td valign="middle" height="16" class="row1"> 
                  <table width="100%" border="0" cellpadding="0" cellspacing="0">
                    <tr valign="bottom"> 
                      <td nowrap>&nbsp;{postrow.PROFILE_IMG} {postrow.PM_IMG} 
                        {postrow.EMAIL_IMG} {postrow.WWW_IMG} {postrow.AIM_IMG} 
                        {postrow.YIM_IMG} {postrow.MSN_IMG} {postrow.ICQ_IMG}</td>
                      <td align="right" nowrap></td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <!-- END postrow -->
            <table border="0" cellspacing="0" cellpadding="0" width="100%">
              <tr>                
                  <td valign="middle">
                    <form method="post" action="{S_POST_DAYS_ACTION}">
                    <table width="100%" border="0" cellpadding="2" cellspacing="1">
                      <tr>
                        <td align="left" width="98%" valign="middle">
                          <table border="0" cellspacing="0" cellpadding="0">
                            <tr> 
                              <td valign="middle"><span class="largetext">&nbsp;&nbsp;{L_DISPLAY_POSTS}:</span></td>
                              <td valign="middle"><span class="largetext">&nbsp;&nbsp;{S_SELECT_POST_DAYS}&nbsp;{S_SELECT_POST_ORDER}</span></td>
                              <td align="left" valign="middle"><span class="largetext"> 
                                &nbsp;<input type="submit" value="{L_GO}" class="liteoption" name="submit" />
                                </span></td>
                            </tr>
                          </table>
			
                        </td>  
                       <td align="right" width="2%" nowrap><!--<a href="{U_POST_NEW_TOPIC}"><img src="{POST_IMG}" border="0" alt="{L_POST_NEW_TOPIC}" align="middle" /></a>&nbsp;&nbsp;&nbsp;--><a href="{U_POST_REPLY_TOPIC}"><img src="{REPLY_IMG}" border="0" alt="{L_POST_REPLY_TOPIC}" align="middle" /></a></td>
                      </tr>
                    </table>
                      </form>
                    </td>                
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
      <td align="left" nowrap><span class="smalltext"><a href="{U_MARK_READ}">{L_MARK_TOPICS_READ}</a><br>
        </span>
        <table cellpadding="0" cellspacing="0" border="0">
          <tr> 
            <td><b><span class="smalltext">Forum Jump:</span></b><br>
              {JUMPBOX}</td>
          </tr>
        </table>
        <span class="smalltext"> </span></td>
      <td align="right"><span class="smalltext">{PAGE_NUMBER}<br>
        <br>
      </span><span class="nav">&lt;&nbsp; <a href="{U_VIEW_OLDER_TOPIC}" class="nav">Last 
      Thread</a>&nbsp;|&nbsp;<a href="{U_VIEW_NEWER_TOPIC}" class="nav">Next Thread 
      </a>&nbsp;&gt;</span><span class="smalltext"> </span></td>
    </tr>
  </table>
  <br>
  <table cellpadding="2" cellspacing="0" border="0" width="98%"  align="center">
    <tr valign="bottom"> 
      <td align="left"><span class="smalltext"><b>Forum Rules:</b></span> <br>
        <table cellpadding="0" cellspacing="0" border="0" align="left">
          <tr> 
            <td class="tableborder"> 
              <table cellpadding="4" cellspacing="1" border="0" align="left">
                <tr> 
                  <td class="row3"><span class="smalltext">{S_AUTH_LIST}</span> 
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>
      
    <td align="right"><span class="gensmall">{S_WATCH_TOPIC}</span><br />
      &nbsp;<br />
      {S_TOPIC_ADMIN}</td>
    </tr>
  </table>

