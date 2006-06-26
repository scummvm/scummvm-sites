<!-- faq_body.tpl (since we got rid of the FAQ from navigation this page should never be displayed anyway-->
 <table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
<table border="0" cellpadding="4" cellspacing="1" width="100%" class="forumline" align="center">
  <tr>
		
    <td class="toprow" align="center" valign="middle"><span class="toprowtext">{L_FAQ_TITLE}</span></td>
	</tr>
	<tr><td class="row1">
<!-- BEGIN faq_block_link -->
<span class="mediumtext"><b>{faq_block_link.BLOCK_TITLE}</b><br /> </span>
<!-- BEGIN faq_row_link -->  
<span class="mediumtext"><a href="{faq_block_link.faq_row_link.U_FAQ_LINK}" class="postlink">{faq_block_link.faq_row_link.FAQ_LINK}</a></span><br />
<!-- END faq_row_link -->
<br />
<!-- END faq_block_link -->
</td></tr>
</table>
    </td>
</tr>
</table>
<!-- BEGIN faq_block -->
<br>
 <table cellpadding="0" cellspacing="0" border="0" width="98%" align="center">
  <tr> 
    <td class="tableborder">
      <table border="0" cellpadding="4" cellspacing="1" width="100%" class="forumline" align="center">
        <tr> 
    <td class="catrow" align="center"><span class="catrowtext">{faq_block.BLOCK_TITLE}</span></td>
  </tr>
  <!-- BEGIN faq_row -->
  <tr> 
    <td align="left" valign="top" class="row1"><span class="mediumtext"><a name="{faq_block.faq_row.U_FAQ_ID}"></a><b>{faq_block.faq_row.FAQ_QUESTION}</b></span><br />
      <span class="mediumtext">{faq_block.faq_row.FAQ_ANSWER}<br />
      <a href="#Top" class="postlink">{L_BACK_TO_TOP}</a></span></td>
  </tr>
  <!-- END faq_row -->
</table>
</td>
</tr>
</table>
<!-- END faq_block -->
<br>
<table width="98%" cellspacing="1" border="0" align="center" cellpadding="4">
  <tr> 
	  <td align="right" valign="middle" nowrap><span class="smalltext">{S_TIMEZONE}</span><br /><br />{JUMPBOX}</td> 
  </tr>
</table>
