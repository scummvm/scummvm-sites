<!-- DEBUG: search_username.tpl starts here -->

<script language="javascript" type="text/javascript">
<!--
function refresh_username(selected_username)
{
	opener.document.forms['post'].username.value = selected_username;
}
//-->
</script>
<form method="post" name="search" action="{S_SEARCH_ACTION}">
  <table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
    <tr> 
      <td class="tableborder"> 
        <table width="100%" border="0" cellspacing="1" cellpadding="4">
          <tr> 
            <td class="catrow" align="center"><span class="catrowtext">{L_SEARCH_USERNAME}</span></td>
          </tr>
          <tr> 
            <td valign="top" class="row1"><span class="mediumtext"><br />
              <input type="text" name="search_username" value="{USERNAME}" />
              &nbsp; 
              <input type="submit" name="search" value="{L_SEARCH}" />
              </span><br />
              <span class="smalltext">{L_SEARCH_EXPLAIN}</span><br />
              <!-- BEGIN switch_select_name -->
              <span class="smalltext">{L_UPDATE_USERNAME}<br />
              <select name="username_list">{S_USERNAME_OPTIONS}
			  </select>
              &nbsp; 
              <input type="submit" onClick="refresh_username(this.form.author_list.options[this.form.author_list.selectedIndex].value);return false;" name="use" value="{L_SELECT}" />
              </span><br />
              <!-- END switch_select_name -->
              <br />
              <span class="mediumtext"><a href="javascript:window.close();">{L_CLOSE_WINDOW}</a></span></td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</form>
