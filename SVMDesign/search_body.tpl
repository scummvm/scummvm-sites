<!-- DEBUG: search_body.tpl starts here -->
<form action="{S_SEARCH_ACTION}" method="POST">
<table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
  <table border="0" cellpadding="4" cellspacing="1" width="100%" class="forumline">
	<tr> 
	  <td class="toprow" colspan="4"><span class="toprowtext">{L_SEARCH_QUERY}</span></td>
	</tr>
	<tr> 
	  <td class="row1" colspan="2" width="50%"><span class="mediumtext">{L_SEARCH_KEYWORDS}:</span><br />
		<span class="smalltext">{L_SEARCH_KEYWORDS_EXPLAIN}</span></td>
	  <td class="row1" colspan="2" valign="top"><span class="mediumtext"> 
		<input type="text" style="width: 300px" name="search_keywords" size="30" />
		<br />
		<input type="radio" name="search_terms" value="any" />
		{L_SEARCH_ANY_TERMS}<br />
		<input type="radio" name="search_terms" value="all" checked="checked" />
		{L_SEARCH_ALL_TERMS}</span></td>
	</tr>
	<tr> 
	  <td class="row1" colspan="2"><span class="mediumtext">{L_SEARCH_AUTHOR}:</span><br />
		<span class="smalltext">{L_SEARCH_AUTHOR_EXPLAIN}</span></td>
	  <td class="row1" colspan="2" valign="middle"><span class="mediumtext"> 
		<input type="text" style="width: 300px" name="search_author" size="30" />
		</span> </td>
	</tr>
	<tr> 
	  <td class="catrow" colspan="4" ><span class="catrowtext">{L_SEARCH_OPTIONS}</span></td>
	</tr>
	<tr> 
	  <td class="row1" align="right"><span class="mediumtext">{L_FORUM}:&nbsp;</span></td>
	  <td class="row1"><span class="mediumtext">
		<select class="post" name="search_forum">{S_FORUM_OPTIONS}
		</select>
		</span></td>
	  <td class="row1" align="right"><span class="mediumtext">{L_RETURN_FIRST}</span></td>
	  <td class="row1"><span class="mediumtext"> 
		<select name="return_chars">{S_CHARACTER_OPTIONS}
		</select>
		{L_CHARACTERS}</span></td>
	</tr>
	<tr> 
	  <td class="row1" align="right"><span class="mediumtext">{L_CATEGORY}:&nbsp;</span></td>
	  <td class="row1"><span class="mediumtext">
		<select class="post" name="search_cat">{S_CATEGORY_OPTIONS}
		</select>
		</span></td>
	  <td class="row1" align="right"><span class="mediumtext">{L_SORT_BY}:&nbsp;</span></td>
	  <td class="row1" valign="middle" nowrap><span class="mediumtext"> 
		<select class="post" name="sort_by">{S_SORT_OPTIONS}
			  
		</select>
		<br />
		<input type="radio" name="sort_dir" value="ASC" />
		{L_SORT_ASCENDING}<br />
		<input type="radio" name="sort_dir" value="DESC" checked="checked" />
		{L_SORT_DESCENDING}</span>&nbsp;</td>
	</tr>
	<tr> 
	  <td class="row1" align="right" nowrap><span class="mediumtext">{L_DISPLAY_RESULTS}:&nbsp;</span></td>
	  <td class="row1" nowrap> 
		<input type="radio" name="show_results" value="posts" />
		<span class="mediumtext">{L_POSTS}
		<input type="radio" name="show_results" value="topics" checked="checked" />
		{L_TOPICS}</span></td>
	  <td class="row1" align="right" nowrap><span class="mediumtext">{L_SEARCH_PREVIOUS}:&nbsp;</span></td>
	  <td class="row1" valign="middle"><span class="mediumtext">
		<select class="post" name="search_time">{S_TIME_OPTIONS}
		</select>
		</span></td>
	</tr>
	<tr> 
	  <td class="catrow" colspan="4" align="center" >	  
		{S_HIDDEN_FIELDS}<input class="liteoption" type="submit" value="{L_SEARCH}" />
	  </td>
	</tr>
  </table>
  </td></tr></table>
  <table width="98%" cellspacing="2" border="0" align="center" cellpadding="2">
    <tr> 
	  <td align="right" valign="middle"><span class="smalltext">{S_TIMEZONE}</span></td>
	</tr>
  </table>
</form>
<table width="98%" border="0" align="center">
  <tr> 
	<td align="right" valign="top">{JUMPBOX}</td>
  </tr>
</table>
