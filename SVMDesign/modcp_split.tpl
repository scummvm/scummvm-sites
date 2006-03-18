
<form method="post" action="{S_SPLIT_ACTION}">
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
  <table width="100%" cellpadding="4" cellspacing="1" border="0">
	      <tr align="right"> 
            <td class="toprow" colspan="3"><span class="toprow">{L_SPLIT_TOPIC}</span></td>
	</tr>
	<tr> 
	  <td class="row1" colspan="3" align="center"><span class="smalltext">{L_SPLIT_TOPIC_EXPLAIN}</span></td>
	</tr>
	<tr> 
	  <td class="row1" nowrap><span class="mediumtext">{L_SPLIT_SUBJECT}</span></td>
	  <td class="row1" colspan="2"><span class="smalltext"> 
		<input type="text" size="35" style="width: 350px" maxlength="100" name="subject" />
		</span></td>
	</tr>
	<tr> 
	  <td class="row1" nowrap><span class="mediumtext">{L_SPLIT_FORUM}</span></td>
	  <td class="row1" colspan="2"><span class="smalltext">{S_FORUM_SELECT}</span></td>
	</tr>
	<tr> 
	  <td class="catrow" colspan="3" height="28"> 
		<table width="60%" cellspacing="0" cellpadding="0" border="0" align="center">
		  <tr> 
			<td width="50%" align="center"> 
			  <input type="submit" name="split_type_all" value="{L_SPLIT_POSTS}" />
			</td>
			<td width="50%" align="center"> 
			  <input type="submit" name="split_type_beyond" value="{L_SPLIT_AFTER}" />
			</td>
		  </tr>
		</table>
	  </td>
	</tr>
	<tr> 
	  <td class="toprow"><span class="toprowtext">{L_AUTHOR}</span></td>
	  <td class="toprow"><span class="toprowtext">{L_MESSAGE}</span></td>
	  <td class="toprow"><span class="toprowtext">{L_SELECT}</span></td>
	</tr>
	<!-- BEGIN postrow -->
	<tr> 
	  <td align="left" valign="top" class="row1"><span class="smalltext"><a name="{postrow.U_POST_ID}"></a>{postrow.POSTER_NAME}</span></td>
	  <td width="100%" valign="top" class="row1"> 
		<table width="100%" cellspacing="0" cellpadding="3" border="0">
		  <tr> 
			<td valign="middle"><img src="templates/SVMDesign/images/icon_minipost.gif" alt="Post image icon"><span class="smalltext">{L_POSTED}: 
			  {postrow.POST_DATE}&nbsp;&nbsp;&nbsp;&nbsp;{L_POST_SUBJECT}: {postrow.POST_SUBJECT}</span></td>
		  </tr>
		  <tr> 
			<td valign="top"> 
			  <hr size="1" />
			  <span class="mediumtext">{postrow.MESSAGE}</span></td> 
		  </tr>
		</table>
	  </td>
	  <td width="5%" align="center" class="row1"><input type="checkbox" name="post_id_list[]" value="{postrow.POST_ID}" /></td>
	</tr>
	<!-- END postrow -->
	<tr> 
	  <td class="catrow" colspan="3" height="28"> 
		<table width="60%" cellspacing="0" cellpadding="0" border="0" align="center">
		  <tr> 
			<td width="50%" align="center"> 
			  <input type="submit" name="split_type_all" value="{L_SPLIT_POSTS}" />
			</td>
			<td width="50%" align="center"> 
			  <input type="submit" name="split_type_beyond" value="{L_SPLIT_AFTER}" />
			  {S_HIDDEN_FIELDS} </td>
		  </tr>
		</table>
	  </td>
	</tr>
  </table>
  </td>
  </tr>
  </table>
  <table width="98%" cellspacing="2" border="0" align="center" cellpadding="2">
    <tr> 
	  <td align="right" valign="top"><span class="smalltext">{S_TIMEZONE}</span></td>
	</tr>
  </table>
</form>
