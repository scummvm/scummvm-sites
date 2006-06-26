<!-- DEBUG: memberlist_body.tpl starts here -->
<form method="post" action="{S_MODE_ACTION}">
  <table width="98%" cellspacing="2" cellpadding="2" border="0" align="center">
    <tr> 
      <td align="right"><span class="mediumtext">{L_SELECT_SORT_METHOD}:&nbsp;{S_MODE_SELECT}&nbsp;&nbsp;{L_ORDER}&nbsp;{S_ORDER_SELECT}&nbsp;&nbsp; 
        <input type="submit" name="submit" value="{L_SUBMIT}" />
        </span></td>
    </tr>
  </table>
  <table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
        <table width="100%" cellpadding="4" cellspacing="1" border="0">
          <tr> 
            <td class="toprow">&nbsp;</td>
            <td class="toprow"> 
              <div align="center"><span class="toprowtext">{L_USERNAME}</span></div>
            </td>
            <td class="toprow"> 
              <div align="center"><span class="toprowtext">{L_EMAIL}</span></div>
            </td>
            <td class="toprow"> 
              <div align="center"><span class="toprowtext">{L_FROM}</span></div>
            </td>
            <td class="toprow"> 
              <div align="center"><span class="toprowtext">{L_JOINED}</span></div>
            </td>
            <td class="toprow"> 
              <div align="center"><span class="toprowtext">{L_POSTS}</span></div>
            </td>
            <td class="toprow"> 
              <div align="center"><span class="toprowtext">{L_WEBSITE}</span></div>
            </td>
          </tr>
          <!-- BEGIN memberrow -->
          <tr> 
            <td class="row1" align="center">&nbsp;{memberrow.PM_IMG}&nbsp;</td>
            <td class="row1" align="center"><span class="mediumtext"><a href="{memberrow.U_VIEWPROFILE}" class="mediumlink">{memberrow.USERNAME}</a></span></td>
            <td class="row1" align="center" valign="middle">&nbsp;{memberrow.EMAIL_IMG}&nbsp;</td>
            <td class="row1" align="center" valign="middle"><span class="mediumtext">{memberrow.FROM}</span></td>
            <td class="row1" align="center" valign="middle"><span class="smalltext">{memberrow.JOINED}</span></td>
            <td class="row1" align="center" valign="middle"><span class="mediumtext">{memberrow.POSTS}</span></td>
            <td class="row1" align="center">&nbsp;{memberrow.WWW_IMG}&nbsp;</td>
          </tr>
          <!-- END memberrow -->
          <tr> 
            <td class="catrow" colspan="7"><span class="catrowtext">&nbsp;</span></td>
          </tr>
        </table>

</td>
</tr>
</table>
  <table width="98%" cellspacing="0" cellpadding="0" border="0" align="center">
    <tr> 
	<td><span class="smalltext">{PAGE_NUMBER}</span></td>
	<td align="right"><span class="smalltext">{S_TIMEZONE}</span><br /><span class="smalltext">{PAGINATION}&nbsp;</span></td>
  </tr>
</table></form>

<table width="98%" cellspacing="2" border="0" align="center">
  <tr> 
	<td valign="top" align="right">{JUMPBOX}</td>
  </tr>
</table>
