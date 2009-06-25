<!-- DEBUG: profile_view_body.tpl starts here -->

<script language="Javascript" type="text/javascript">
<!--
function create_icq_subsilver(icq_user_addr, icq_status_img, icq_add_img)
{
	if( icq_user_addr.length && icq_user_addr.indexOf("&nbsp;") == -1 )
	{
		document.write('<table width="59" border="0" cellspacing="0" cellpadding="0"><tr><td nowrap="nowrap" style=" background-image: url(\'' + icq_add_img + '\'); background-repeat: no-repeat"><img src="images/spacer.gif" width="3" height="18" alt = "">' + icq_status_img + '<a href="http://wwp.icq.com/scripts/search.dll?to=' + icq_user_addr + '"><img src="images/spacer.gif" width="35" height="18" border="0" alt="{L_ICQ_NUMBER}"><\/a><\/td><\/tr><\/table>');
	}
}
//-->
</script>

<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
      <table cellpadding="4" cellspacing="1" border="0"  width="100%">
        <tr> 
          <td colspan="2" class="toprow"> 
            <table width="100%" border="0" cellpadding="0" cellspacing="0">
              <tr> 
                <td align="left"><span class="toprowtext">{L_VIEWING_PROFILE}</span></td>
                <td align="right"><a href="{U_SEARCH_USER}" class="toprowlink">{L_SEARCH_USER_POSTS}</a></td>
              </tr>
            </table>
          </td>
        </tr>
        <tr> 
          <td class="row1"><b><span class="largetext">{L_JOINED}:&nbsp;</span></b></td>
          <td class="row1"><span class="largetext">{JOINED}</span></td>
        </tr>
        <tr> 
          <td class="row1"><b><span class="largetext">{L_ABOUT_USER}</span></b></td>
          <td class="row1"><span class="largetext">{POSTER_RANK}</span>&nbsp;{AVATAR_IMG}<br>
            <span class="mediumlink">{L_CONTACT} {USERNAME}</span></td>
        </tr>
        <tr> 
          <td class="row1"><b><span class="largetext">{L_TOTAL_POSTS}:</span></b></td>
          <td class="row1"><span class="largetext">{POSTS}</span>&nbsp;<span class="largetext">[{POST_PERCENT_STATS} 
            / {POST_DAY_STATS}]</span> </td>
        </tr>
        <tr> 
          <td class="row1"><b><span class="largetext">{L_EMAIL_ADDRESS}:</span></b></td>
          <td class="row1"><span class="largetext">{EMAIL_IMG}</span></td>
        </tr>
        <tr> 
          <td class="row1"><b><span class="largetext">{L_WEBSITE}:</span></b></td>
          <td class="row1"><span class="largetext">{WEBSITE}</span></td>
        </tr>
        <tr> 
          <td class="row1"><b><span class="largetext">{L_ICQ_NUMBER}:</span></b></td>
          <td class="row1"><span class="largetext"> {ICQ_IMG}</span></td>
        </tr>
        <tr> 
          <td class="row1"><b><span class="largetext">{L_AIM}:</span></b></td>
          <td class="row1"><span class="largetext">{AIM_IMG}</span></td>
        </tr>
        <tr> 
          <td class="row1"><b><span class="largetext">{L_YAHOO}:</span></b></td>
          <td class="row1"><span class="largetext">{YIM_IMG}</span></td>
        </tr>
        <tr> 
          <td class="row1"><b><span class="largetext">{L_MESSENGER}:</span></b></td>
          <td class="row1"><span class="largetext">{MSN}</span></td>
        </tr>
        <tr> 
          <td class="row1"><b><span class="largetext">{L_PM}:</span></b></td>
          <td class="row1"><span class="largetext">{PM_IMG}</span></td>
        </tr>
        <tr> 
          <td class="row1"><b><span class="largetext">{L_LOCATION}:&nbsp;</span></b></td>
          <td class="row1"><span class="largetext">{LOCATION}</span></td>
        </tr>
        <tr> 
          <td class="row1"><b><span class="largetext">{L_OCCUPATION}:&nbsp;</span></b></td>
          <td class="row1"><span class="largetext">{OCCUPATION}</span></td>
        </tr>
        <tr> 
          <td class="row1"><b><span class="largetext">{L_INTERESTS}:</span></b></td>
          <td class="row1"><span class="largetext">{INTERESTS}</span></td>
        </tr>
        <tr> 
          <td align="center" colspan="2" class="toprow">&nbsp;</td>
        </tr>
      </table>
    </td>
</tr>
</table>
<br>
<p>&nbsp;</p>
<table width="100%" border="0" cellspacing="0" cellpadding="0" align="center">
  <tr> 
	<td align="right"><br>{JUMPBOX}</td>
  </tr>
</table>
