<!-- DEBUG: profile_avatar_gallery.tpl starts here -->
<form action="{S_PROFILE_ACTION}" method="post">
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
<table border="0" cellpadding="4" cellspacing="1" width="100%">
	<tr> 
	        <td class="catrow" colspan="{S_COLSPAN}" valign="middle" align="center"><span class="catrowtext">{L_AVATAR_GALLERY}</span></td>
	</tr>
	<tr> 
	        <td class="row1" align="center" valign="middle" colspan="6"><span class="mediumtext">{L_CATEGORY}:&nbsp; 
              {S_CATEGORY_SELECT}&nbsp;<input type="submit" value="{L_GO}" name="avatargallery" /></span></td>
	</tr>
	<!-- BEGIN avatar_row -->
	<tr> 
	<!-- BEGIN avatar_column -->
		<td class="row1" align="center"><img src="{avatar_row.avatar_column.AVATAR_IMAGE}" alt="Avatar" /></td>
	<!-- END avatar_column -->
	</tr>
	<tr>
	<!-- BEGIN avatar_option_column -->
		<td class="row1" align="center"><input type="radio" name="avatarselect" value="{avatar_row.avatar_option_column.S_OPTIONS_AVATAR}" /></td>
	<!-- END avatar_option_column -->
	</tr>

	<!-- END avatar_row -->
	<tr> 
	        <td class="catrow" colspan="{S_COLSPAN}" align="center">{S_HIDDEN_FIELDS} 
              <input type="submit" name="submitavatar" value="{L_SELECT_AVATAR}" class="mainoption" />
		&nbsp;&nbsp; 
		<input type="submit" name="cancelavatar" value="{L_RETURN_PROFILE}" class="liteoption" />
	  </td>
	</tr>
  </table>
  </td>
  </tr>
  </table>
</form>
