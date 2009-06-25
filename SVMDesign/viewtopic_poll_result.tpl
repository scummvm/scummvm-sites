<!-- DEBUG: viewtopic_poll_results.tpl starts here --> 
<tr> 
  <td class="row1" colspan="3"><br clear="all">
        <table cellpadding="0" cellspacing="0" border="0" align="center">
        <tr> 
    <td class="tableborder">
	      <table cellspacing="1" cellpadding="4" border="0" align="center">
            <tr> 
		<td colspan="4" align="center" class="catrow"><span class="catrowtext"><b>{POLL_QUESTION}</b></span></td>
	  </tr>
	  <tr> 
		<td align="center" class="row1"> 
		  <table cellspacing="0" cellpadding="2" border="0">
			<!-- BEGIN poll_option -->
			<tr> 
			  <td><span class="mediumtext">{poll_option.POLL_OPTION_CAPTION}</span></td>
			  <td> 
				<table cellspacing="0" cellpadding="0" border="0">
				  <tr> 
					<td><img src="templates/SVMDesign/images/vote_lcap.gif" width="4" alt="" height="12"></td>
					<td><img src="{poll_option.POLL_OPTION_IMG}" width="{poll_option.POLL_OPTION_IMG_WIDTH}" height="12" alt="{poll_option.POLL_OPTION_PERCENT}"></td>
					<td><img src="templates/SVMDesign/images/vote_rcap.gif" width="4" alt="" height="12"></td>
				  </tr>
				</table>
			  </td>
			  <td align="center"><b><span class="mediumtext">&nbsp;{poll_option.POLL_OPTION_PERCENT}&nbsp;</span></b></td>
			  <td align="center"><span class="mediumtext">[ {poll_option.POLL_OPTION_RESULT} ]</span></td>
			</tr>
			<!-- END poll_option -->
		  </table>
		</td>
	  </tr>
	  <tr> 
		<td colspan="4" align="center" class="row1"><span class="mediumtext"><b>Total Votes : {TOTAL_VOTES}</b></span></td>
	  </tr>
	</table>
	</td>
	</tr>
	</table>
	<br clear="all">
  </td>
</tr>
