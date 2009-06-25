<!-- DEBUG: posting_body.tpl starts here -->

<script language="JavaScript" type="text/javascript">
<!--
// bbCode control by
// subBlue design
// www.subBlue.com

// Startup variables
var imageTag = false;
var theSelection = false;

// Check for Browser & Platform for PC & IE specific bits
// More details from: http://www.mozilla.org/docs/web-developer/sniffer/browser_type.html
var clientPC = navigator.userAgent.toLowerCase(); // Get client info
var clientVer = parseInt(navigator.appVersion); // Get browser version

var is_ie = ((clientPC.indexOf("msie") != -1) && (clientPC.indexOf("opera") == -1));
var is_nav  = ((clientPC.indexOf('mozilla')!=-1) && (clientPC.indexOf('spoofer')==-1)
                && (clientPC.indexOf('compatible') == -1) && (clientPC.indexOf('opera')==-1)
                && (clientPC.indexOf('webtv')==-1) && (clientPC.indexOf('hotjava')==-1));

var is_win   = ((clientPC.indexOf("win")!=-1) || (clientPC.indexOf("16bit") != -1));
var is_mac    = (clientPC.indexOf("mac")!=-1);


// Helpline messages
b_help = "{L_BBCODE_B_HELP}";
i_help = "{L_BBCODE_I_HELP}";
u_help = "{L_BBCODE_U_HELP}";
q_help = "{L_BBCODE_Q_HELP}";
c_help = "{L_BBCODE_C_HELP}";
l_help = "{L_BBCODE_L_HELP}";
o_help = "{L_BBCODE_O_HELP}";
p_help = "{L_BBCODE_P_HELP}";
w_help = "{L_BBCODE_W_HELP}";
a_help = "{L_BBCODE_A_HELP}";
s_help = "{L_BBCODE_S_HELP}";
f_help = "{L_BBCODE_F_HELP}";

// Define the bbCode tags
bbcode = new Array();
bbtags = new Array('[b]','[/b]','[i]','[/i]','[u]','[/u]','[quote]','[/quote]','[code]','[/code]','[list]','[/list]','[list=]','[/list]','[img]','[/img]','[url]','[/url]');
imageTag = false;

// Shows the help messages in the helpline window
function helpline(help) {
	document.post.helpbox.value = eval(help + "_help");
}


// Replacement for arrayname.length property
function getarraysize(thearray) {
	for (i = 0; i < thearray.length; i++) {
		if ((thearray[i] == "undefined") || (thearray[i] == "") || (thearray[i] == null))
			return i;
		}
	return thearray.length;
}

// Replacement for arrayname.push(value) not implemented in IE until version 5.5
// Appends element to the array
function arraypush(thearray,value) {
	thearray[ getarraysize(thearray) ] = value;
}

// Replacement for arrayname.pop() not implemented in IE until version 5.5
// Removes and returns the last element of an array
function arraypop(thearray) {
	thearraysize = getarraysize(thearray);
	retval = thearray[thearraysize - 1];
	delete thearray[thearraysize - 1];
	return retval;
}


function checkForm() {

	formErrors = false;    

	if (document.post.message.value.length < 2) {
		formErrors = "{L_EMPTY_MESSAGE}";
	}

	if (formErrors) {
		alert(formErrors);
		return false;
	} else {
		bbstyle(-1);
		//formObj.preview.disabled = true;
		//formObj.submit.disabled = true;
		return true;
	}
}

function emoticon(text) {
	text = ' ' + text + ' ';
	if (document.post.message.createTextRange && document.post.message.caretPos) {
		var caretPos = document.post.message.caretPos;
		caretPos.text = caretPos.text.charAt(caretPos.text.length - 1) == ' ' ? text + ' ' : text;
		document.post.message.focus();
	} else {
	document.post.message.value  += text;
	document.post.message.focus();
	}
}

function bbfontstyle(bbopen, bbclose) {
	if ((clientVer >= 4) && is_ie && is_win) {
		theSelection = document.selection.createRange().text;
		if (!theSelection) {
			document.post.message.value += bbopen + bbclose;
			document.post.message.focus();
			return;
		}
		document.selection.createRange().text = bbopen + theSelection + bbclose;
		document.post.message.focus();
		return;
	} else {
		document.post.message.value += bbopen + bbclose;
		document.post.message.focus();
		return;
	}
	storeCaret(document.post.message);
}


function bbstyle(bbnumber) {

	donotinsert = false;
	theSelection = false;
	bblast = 0;

	if (bbnumber == -1) { // Close all open tags & default button names
		while (bbcode[0]) {
			butnumber = arraypop(bbcode) - 1;
			document.post.message.value += bbtags[butnumber + 1];
			buttext = eval('document.post.addbbcode' + butnumber + '.value');
			eval('document.post.addbbcode' + butnumber + '.value ="' + buttext.substr(0,(buttext.length - 1)) + '"');
		}
		imageTag = false; // All tags are closed including image tags :D
		document.post.message.focus();
		return;
	}

	if ((clientVer >= 4) && is_ie && is_win)
		theSelection = document.selection.createRange().text; // Get text selection
		
	if (theSelection) {
		// Add tags around selection
		document.selection.createRange().text = bbtags[bbnumber] + theSelection + bbtags[bbnumber+1];
		document.post.message.focus();
		theSelection = '';
		return;
	}
	
	// Find last occurance of an open tag the same as the one just clicked
	for (i = 0; i < bbcode.length; i++) {
		if (bbcode[i] == bbnumber+1) {
			bblast = i;
			donotinsert = true;
		}
	}

	if (donotinsert) {		// Close all open tags up to the one just clicked & default button names
		while (bbcode[bblast]) {
				butnumber = arraypop(bbcode) - 1;
				document.post.message.value += bbtags[butnumber + 1];
				buttext = eval('document.post.addbbcode' + butnumber + '.value');
				eval('document.post.addbbcode' + butnumber + '.value ="' + buttext.substr(0,(buttext.length - 1)) + '"');
				imageTag = false;
			}
			document.post.message.focus();
			return;
	} else { // Open tags
	
		if (imageTag && (bbnumber != 14)) {		// Close image tag before adding another
			document.post.message.value += bbtags[15];
			lastValue = arraypop(bbcode) - 1;	// Remove the close image tag from the list
			document.post.addbbcode14.value = "Img";	// Return button back to normal state
			imageTag = false;
		}
		
		// Open tag
		document.post.message.value += bbtags[bbnumber];
		if ((bbnumber == 14) && (imageTag == false)) imageTag = 1; // Check to stop additional tags after an unclosed image tag
		arraypush(bbcode,bbnumber+1);
		eval('document.post.addbbcode'+bbnumber+'.value += "*"');
		document.post.message.focus();
		return;
	}
	storeCaret(document.post.message);
}

// Insert at Caret position. Code from
// http://www.faqts.com/knowledge_base/view.phtml/aid/1052/fid/130
function storeCaret(textEl) {
	if (textEl.createTextRange) textEl.caretPos = document.selection.createRange().duplicate();
}

//-->
</script>
<!-- BEGIN switch_not_privmsg -->
<table cellpadding="2" cellspacing="0" border="0" width="98%"  align="center">
  <tr> 
	  <td><img src="templates/SVMDesign/images/folder_new.gif" border="0" alt="Folder"></td>
		<td style="vertical-align: middle;" width="100%"><span 
		class="largetext"><a href="{U_INDEX}" class="largelink"><b>Forum Index</b></a>
        &gt; <a href="{U_VIEW_FORUM}" class="largelink"><b>{FORUM_NAME}</b></a></span>
		</td>
	</tr>  
</table>
<!-- END switch_not_privmsg -->
<!-- BEGIN switch_privmsg -->
<table border="0" cellspacing="0" cellpadding="0" align="center" width="100%">
  <tr> 
    <td valign="top" align="center" width="100%"> 
      <table cellspacing="2" cellpadding="2" border="0">
		  <tr valign="middle"> 
		  <td>{INBOX_IMG}</td>
		  <td><span class="smalltext">{INBOX}&nbsp;&nbsp;</span></td>
		  <td>{SENTBOX_IMG}</td>
		  <td><span class="smalltext">{SENTBOX}&nbsp;&nbsp;</span></td>
		  <td>{OUTBOX_IMG}</td>
		  <td><span class="smalltext">{OUTBOX}&nbsp;&nbsp;</span></td>
		  <td>{SAVEBOX_IMG}</td>
		  <td><span class="smalltext">{SAVEBOX}&nbsp;&nbsp;</span></td>
		</tr>
      </table>
    </td>
  </tr>
</table>
<br clear="all">
<!-- END switch_privmsg -->
<form action="{S_POST_ACTION}" method="post" name="post" onsubmit="return checkForm(this)">
  {POST_PREVIEW_BOX} {ERROR_BOX}   
  <table width="98%" cellpadding="0" cellspacing="0" align="center">
    <tr> 
      <td class="tableborder"> 
        <table border="0" cellpadding="3" cellspacing="1" width="100%">
          <tr> 
            <td class="toprow" colspan="2"><b>{L_POST_A}</b></td>
          </tr>
          <!-- BEGIN switch_username_select -->
          <tr> 
            <td class="row1"><b>{L_USERNAME}</b></td>
            <td class="row1">
              <input type="text" class="post" tabindex="1" name="username" size="25" maxlength="25" value="{USERNAME}">
              </td>
          </tr>
          <!-- END switch_username_select -->
          <!-- This is for private messaging -->
          <!-- BEGIN switch_privmsg -->
          <tr> 
            <td class="row1"><b>{L_USERNAME}</b></td>
            <td class="row1">
              <input type="text"  class="post" name="username" maxlength="25" size="25" tabindex="1" value="{USERNAME}">
              &nbsp; 
              <input type="submit" name="usersubmit" value="{L_FIND_USERNAME}" class="liteoption" onClick="window.open('{U_SEARCH_USER}', '_phpbbsearch', 'HEIGHT=250,resizable=yes,WIDTH=400');return false;">
              </td>
          </tr>
          <!-- END switch_privmsg -->
          <tr> 
            <td class="row1" width="22%"><b>{L_SUBJECT}</b></td>
            <td class="row1" width="78%">
              <input type="text" name="subject" size="45" maxlength="60" style="width:450px" tabindex="2" class="post" value="{SUBJECT}">
              </td>
          </tr>
          <tr> 
            <td class="row1" valign="top"> 
              <table width="100%" border="0" cellspacing="0" cellpadding="1">
                <tr> 
                  <td><b>{L_MESSAGE_BODY}</b></td>
                </tr>
                <tr> 
                  <td valign="middle" align="center"> <br>
                    <table width="100" border="0" cellspacing="0" cellpadding="5">
                      <tr align="center"> 
                        <td colspan="{S_SMILIES_COLSPAN}"><b>{L_EMOTICONS}</b></td>
                      </tr>
                      <!-- BEGIN smilies_row -->
                      <tr align="center" valign="middle"> 
                        <!-- BEGIN smilies_col -->
                        <td><a href="javascript:emoticon('{smilies_row.smilies_col.SMILEY_CODE}')"><img src="{smilies_row.smilies_col.SMILEY_IMG}" border="0" alt="{smilies_row.smilies_col.SMILEY_DESC}" title="{smilies_row.smilies_col.SMILEY_DESC}"></a></td>
                        <!-- END smilies_col -->
                      </tr>
                      <!-- END smilies_row -->
                      <!-- BEGIN switch_smilies_extra -->
                      <tr align="center"> 
                        <td colspan="{S_SMILIES_COLSPAN}"><span  class="nav"><a href="{U_MORE_SMILIES}" onclick="window.open('{U_MORE_SMILIES}', '_phpbbsmilies', 'HEIGHT=300,resizable=yes,scrollbars=yes,WIDTH=250');return false;" target="_phpbbsmilies" class="nav">{L_MORE_SMILIES}</a></span></td>
                      </tr>
                      <!-- END switch_smilies_extra -->
                    </table>
                  </td>
                </tr>
              </table>
            </td>
            <td class="row1" valign="top">
              <table width="450" border="0" cellspacing="0" cellpadding="2">
                <tr align="center" valign="middle"> 
                  <td>
                    <input type="button" class="button" accesskey="b" name="addbbcode0" value=" B " style="font-weight:bold; width: 30px" onClick="bbstyle(0)" onMouseOver="helpline('b')">
                    </td>
                  <td>
                    <input type="button" class="button" accesskey="i" name="addbbcode2" value=" i " style="font-style:italic; width: 30px" onClick="bbstyle(2)" onMouseOver="helpline('i')">
                    </td>
                  <td>
                    <input type="button" class="button" accesskey="u" name="addbbcode4" value=" u " style="text-decoration: underline; width: 30px" onClick="bbstyle(4)" onMouseOver="helpline('u')">
                    </td>
                  <td>
                    <input type="button" class="button" accesskey="q" name="addbbcode6" value="Quote" style="width: 50px" onClick="bbstyle(6)" onMouseOver="helpline('q')">
                    </td>
                  <td>
                    <input type="button" class="button" accesskey="c" name="addbbcode8" value="Code" style="width: 40px" onClick="bbstyle(8)" onMouseOver="helpline('c')">
                    </td>
                  <td>
                    <input type="button" class="button" accesskey="l" name="addbbcode10" value="List" style="width: 40px" onClick="bbstyle(10)" onMouseOver="helpline('l')">
                    </td>
                  <td>
                    <input type="button" class="button" accesskey="o" name="addbbcode12" value="List=" style="width: 40px" onClick="bbstyle(12)" onMouseOver="helpline('o')">
                    </td>
                  <td>
                    <input type="button" class="button" accesskey="p" name="addbbcode14" value="Img" style="width: 40px"  onClick="bbstyle(14)" onMouseOver="helpline('p')">
                    </td>
                  <td>
                    <input type="button" class="button" accesskey="w" name="addbbcode16" value="URL" style="text-decoration: underline; width: 40px" onClick="bbstyle(16)" onMouseOver="helpline('w')">
                    </td>
                </tr>
                <tr> 
                  <td colspan="9"> 
                    <table width="100%" border="0" cellspacing="0" cellpadding="0">
                      <tr> 
                        <td>&nbsp;{L_FONT_COLOR}: 
                          <select name="addbbcode18" onChange="bbfontstyle('[color=' + this.form.addbbcode18.options[this.form.addbbcode18.selectedIndex].value + ']', '[/color]')" onMouseOver="helpline('s')">
                            <option style="color:black; background-color: #FFFFFF " value="{T_FONTCOLOR1}">{L_COLOR_DEFAULT}</option>
                            <option style="color:darkred; background-color: #DEE3E7" value="darkred">{L_COLOR_DARK_RED}</option>
                            <option style="color:red; background-color: #DEE3E7" value="red">{L_COLOR_RED}</option>
                            <option style="color:orange; background-color: #DEE3E7" value="orange">{L_COLOR_ORANGE}</option>
                            <option style="color:brown; background-color: #DEE3E7" value="brown">{L_COLOR_BROWN}</option>
                            <option style="color:yellow; background-color: #DEE3E7" value="yellow">{L_COLOR_YELLOW}</option>
                            <option style="color:green; background-color: #DEE3E7" value="green">{L_COLOR_GREEN}</option>
                            <option style="color:olive; background-color: #DEE3E7" value="olive">{L_COLOR_OLIVE}</option>
                            <option style="color:cyan; background-color: #DEE3E7" value="cyan">{L_COLOR_CYAN}</option>
                            <option style="color:blue; background-color: #DEE3E7" value="blue">{L_COLOR_BLUE}</option>
                            <option style="color:darkblue; background-color: #DEE3E7" value="darkblue">{L_COLOR_DARK_BLUE}</option>
                            <option style="color:indigo; background-color: #DEE3E7" value="indigo">{L_COLOR_INDIGO}</option>
                            <option style="color:violet; background-color: #DEE3E7" value="violet">{L_COLOR_VIOLET}</option>
                            <option style="color:white; background-color: #DEE3E7" value="white">{L_COLOR_WHITE}</option>
                            <option style="color:black; background-color: #DEE3E7" value="black">{L_COLOR_BLACK}</option>
                          </select>
                          &nbsp;{L_FONT_SIZE}:
                          <select name="addbbcode20" onChange="bbfontstyle('[size=' + this.form.addbbcode20.options[this.form.addbbcode20.selectedIndex].value + ']', '[/size]')" onMouseOver="helpline('f')">
                            <option value="7">{L_FONT_TINY}</option>
                            <option value="9">{L_FONT_SMALL}</option>
                            <option value="12" selected>{L_FONT_NORMAL}</option>
                            <option value="18">{L_FONT_LARGE}</option>
                            <option  value="24">{L_FONT_HUGE}</option>
                          </select>
                          </td>
                        <td nowrap align="right"><a href="javascript:bbstyle(-1)" onMouseOver="helpline('a')">{L_BBCODE_CLOSE_TAGS}</a></td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr> 
                  <td colspan="9">
                    <input type="text" name="helpbox" size="45" maxlength="100" style="width:450px;" value="{L_STYLES_TIP}">
                    </td>
                </tr>
                <tr> 
                  <td colspan="9">
                    <textarea name="message" rows="15" cols="35" wrap="virtual" style="width:450px" tabindex="3" class="post" onselect="storeCaret(this);" onclick="storeCaret(this);" onkeyup="storeCaret(this);">{MESSAGE}</textarea>
                    </td>
                </tr>
              </table>
              </td>
          </tr>
          <tr> 
            <td class="row1" valign="top"><b>{L_OPTIONS}</b><br>
              {HTML_STATUS}<br>
              {BBCODE_STATUS}<br>
              {SMILIES_STATUS}</td>
            <td class="row1">
              <table cellspacing="0" cellpadding="1" border="0">
                <!-- BEGIN switch_html_checkbox -->
                <tr> 
                  <td> 
                    <input type="checkbox" name="disable_html" {S_HTML_CHECKED}>
                  </td>
                  <td>{L_DISABLE_HTML}</td>
                </tr>
                <!-- END switch_html_checkbox -->
                <!-- BEGIN switch_bbcode_checkbox -->
                <tr> 
                  <td> 
                    <input type="checkbox" name="disable_bbcode" {S_BBCODE_CHECKED}>
                  </td>
                  <td>{L_DISABLE_BBCODE}</td>
                </tr>
                <!-- END switch_bbcode_checkbox -->
                <!-- BEGIN switch_smilies_checkbox -->
                <tr> 
                  <td> 
                    <input type="checkbox" name="disable_smilies" {S_SMILIES_CHECKED}>
                  </td>
                  <td>{L_DISABLE_SMILIES}</td>
                </tr>
                <!-- END switch_smilies_checkbox -->
                <!-- BEGIN switch_signature_checkbox -->
                <tr> 
                  <td> 
                    <input type="checkbox" name="attach_sig" {S_SIGNATURE_CHECKED}>
                  </td>
                  <td>{L_ATTACH_SIGNATURE}</td>
                </tr>
                <!-- END switch_signature_checkbox -->
                <!-- BEGIN switch_notify_checkbox -->
                <tr> 
                  <td> 
                    <input type="checkbox" name="notify" {S_NOTIFY_CHECKED}>
                  </td>
                  <td>{L_NOTIFY_ON_REPLY}</td>
                </tr>
                <!-- END switch_notify_checkbox -->
                <!-- BEGIN switch_delete_checkbox -->
                <tr> 
                  <td> 
                    <input type="checkbox" name="delete">
                  </td>
                  <td>{L_DELETE_POST}</td>
                </tr>
                <!-- END switch_delete_checkbox -->
                <!-- BEGIN switch_type_toggle -->
                <tr> 
                  <td></td>
                  <td>{S_TYPE_TOGGLE}</td>
                </tr>
                <!-- END switch_type_toggle -->
              </table>
            </td>
          </tr>
          {POLLBOX} 
          <tr> 
            <td class="toprow" colspan="2" align="center"> {S_HIDDEN_FORM_FIELDS} 
              <input type="submit" accesskey="s" tabindex="6" name="post" class="mainoption" value="{L_SUBMIT}">
              <input type="submit" tabindex="5" name="preview" class="mainoption" value="{L_PREVIEW}">
              &nbsp; </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
  <table width="100%" cellspacing="2" border="0" align="center" cellpadding="2">
    <tr> 
      <td align="right" valign="top">{S_TIMEZONE}</td>
    </tr>
  </table>
</form>
<table width="100%" cellspacing="2" border="0" align="center">
  <tr> 
    <td valign="top" align="right">{JUMPBOX}</td>
  </tr>
</table>
{TOPIC_REVIEW_BOX} 
