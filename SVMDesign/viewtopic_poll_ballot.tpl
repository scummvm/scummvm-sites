<!-- DEBUG: viewtopic_poll_ballot.tpl starts here -->
			<tr>
				<td colspan="3" class="row1"><br clear="all" /><form method="POST" action="{S_POLL_ACTION}">
				
      <table cellpadding="0" cellspacing="0" border="0" align="center" width="100%">
        <tr> 
    <td class="tableborder">				
            <table cellspacing="1" cellpadding="4" border="0" align="center" width="100%">
              <tr>
						<td align="center" class="catrow"><span class="catrowtext"><b>{POLL_QUESTION}</b></span></td>
					</tr>
					<tr>
						<td align="center" class="row1"><table cellspacing="0" cellpadding="2" border="0">
							<!-- BEGIN poll_option -->
							<tr>
								<td><input type="radio" name="vote_id" value="{poll_option.POLL_OPTION_ID}" />&nbsp;</td>
								<td><span class="smalltext">{poll_option.POLL_OPTION_CAPTION}</span></td>
							</tr>
							<!-- END poll_option -->
						</table></td>
					</tr>
					<tr>
						<td align="center" class="row1">
			<input type="submit" name="submit" value="{L_SUBMIT_VOTE}" />
		  </td>
					</tr>
					<tr>
						
		  <td align="center" class="row1"><b><a href="{U_VIEW_RESULTS}" class="smalllink">{L_VIEW_RESULTS}</a></b></td>
					</tr>
				</table>
				</td></tr></table>
				
      <br>
      {S_HIDDEN_FIELDS} 
    </form></td>
			</tr>
