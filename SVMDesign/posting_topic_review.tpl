<!-- DEBUG: posting_review_body.tpl starts here -->

<!-- BEGIN switch_inline_mode -->
 <table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
<table border="0" cellpadding="3" cellspacing="1" width="100%" class="forumline">
	<tr> 
	  
	<td class="catrow" height="28" align="center"><b><span class="catrowtext">{L_TOPIC_REVIEW}</span></b></td>
	</tr>
	<tr>
		<td class="row1"><iframe width="100%" height="300" src="{U_REVIEW_TOPIC}" >
<!-- END switch_inline_mode -->
 <table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
	  <table border="0" cellpadding="3" cellspacing="1" width="100%" class="forumline" style="border: 0px #006699 solid ">
        <tr> 
          <td class="row1" width="22%" height="26">{L_AUTHOR}</td>
          <td class="row1">{L_MESSAGE}</td>
        </tr>
        <!-- BEGIN postrow -->
        <tr> 
          <td width="22%" align="left" valign="top" class="row1"><span class="name"><a name="{postrow.U_POST_ID}"></a><b>{postrow.POSTER_NAME}</b></span></td>
          <td class="row1" height="28" valign="top">
            <table width="100%" border="0" cellspacing="0" cellpadding="0">
              <tr> 
                <td width="100%"><img src="{postrow.MINI_POST_IMG}" alt="{postrow.L_MINI_POST_ALT}" title="{postrow.L_MINI_POST_ALT}" border="0" /><span class="postdetails">{L_POSTED}: 
                  {postrow.POST_DATE}&nbsp;&nbsp;&nbsp;&nbsp;{L_POST_SUBJECT}: 
                  {postrow.POST_SUBJECT}</span></td>
              </tr>
              <tr> 
                <td colspan="2">
                  <hr />
                </td>
              </tr>
              <tr> 
                <td colspan="2"><span class="postbody">{postrow.MESSAGE}</span></td>
              </tr>
            </table>
          </td>
        </tr>
        <!-- END postrow -->
      </table>
</td></tr></table>
<!-- BEGIN switch_inline_mode -->
		</iframe></td>
	</tr>
</table>
</td>
</tr>
</table>
<!-- END switch_inline_mode -->
