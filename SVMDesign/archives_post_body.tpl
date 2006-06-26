<!-- DEBUG: archives_post_body.tpl starts here -->
<script language="Javascript" type="text/javascript">
<!--
function create_icq_subsilver(icq_user_addr, icq_status_img, icq_add_img)
{
	if( icq_user_addr.length && icq_user_addr.indexOf("&nbsp;") == -1 )
	{
		document.write('<table width="59" border="0" cellspacing="0" cellpadding="0"><tr><td nowrap="nowrap" style=" background-image: url(\'' + icq_add_img + '\'); background-repeat: no-repeat"><img src="images/spacer.gif" width="3" height="18" alt = "">' + icq_status_img + '<a href="http://wwp.icq.com/scripts/search.dll?to=' + icq_user_addr + '"><img src="images/spacer.gif" width="35" height="18" border="0" alt="{L_ICQ_NUMBER}" /></a></td></tr></table>');
	}
}
//-->
</script>
<br>
<table cellpadding="2" cellspacing="0" border="0" width="98%"  align="center">
  <tr> 
    <td valign="top" align="left"><img src="templates/LastCrusade/images/folder_new.gif" border="0" align="absmiddle"> 
        <span class="largetext"><a href="index.php" class="largelink"><b>{SITENAME}</b></a> &gt;
        <a class="largelink" href="{U_VIEW_FORUM}"><b>Archives: {FORUM_NAME}</b>
</a> &gt; <B>{TOPIC_TITLE}</B></span><br>
      <b><span class="smalltext">{PAGINATION}<br>
      </span></b></td>
  </tr>
</table>
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder"> 
      <table border="0" cellpadding="0" cellspacing="0" width="100%">
        {POLL_DISPLAY} 
        <tr> 
          <td class="toprow" nowrap > <span class="toprowtext"> </span> 
            <table width="100%" border="0" cellspacing="0" cellpadding="2">
              <tr> 
                <td width="186"><span class="toprowtext">&nbsp;&nbsp;{L_AUTHOR} 
                  </span></td>
                <td><span class="toprowtext">&nbsp;&nbsp;&nbsp;Thread</span></td>
                <td align="right"><a href="{U_POST_NEW_TOPIC}"><img src="{POST_IMG}" border="0" alt="{L_POST_NEW_TOPIC}" align="middle" /></a>&nbsp;&nbsp;&nbsp;<a href="{U_POST_REPLY_TOPIC}"><img src="{REPLY_IMG}" border="0" alt="{L_POST_REPLY_TOPIC}" align="middle" /></a></td>
              </tr>
            </table>
          </td>
        </tr>
        <!-- BEGIN postrow -->
        <tr align="center"> 
          <td class="tableborder" > 
            <table width="100%" border="0" cellspacing="1" cellpadding="4">
              <tr> 
                <td width="186" valign="top" class="row3" nowrap> <span class="largetext"><a name="{postrow.U_POST_ID}"></a><b>{postrow.POSTER_NAME}</b></span><br />
                  <span class="smalltext">{postrow.POSTER_RANK}<br />
                  <br />
                  {postrow.POSTER_FROM}</span></td>
                <td valign="top" class="row3"> <span class="smalltext"><b>{postrow.POST_SUBJECT}</b></span> 
                  <p><span class="largetext">{postrow.MESSAGE}</span></p>
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
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
