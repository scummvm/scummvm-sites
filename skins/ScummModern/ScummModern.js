// MediaWiki JavaScript support functions
// scummmodern version
// changetext now uses innerHTML instead
// TODO: Depricate this and use jquery 
// @see https://www.mediawiki.org/wiki/ResourceLoader/Legacy_JavaScript
// @see https://www.mediawiki.org/wiki/JavaScript

var clientPC = navigator.userAgent.toLowerCase(); // Get client info
var is_gecko = /gecko/.test( clientPC ) &&
	!/khtml|spoofer|netscape\/7\.0/.test(clientPC);
var webkit_match = clientPC.match(/applewebkit\/(\d+)/);
if (webkit_match) {
	var is_safari = clientPC.indexOf('applewebkit') != -1 &&
		clientPC.indexOf('spoofer') == -1;
	var is_safari_win = is_safari && clientPC.indexOf('windows') != -1;
	var webkit_version = parseInt(webkit_match[1]);
}
var is_khtml = navigator.vendor == 'KDE' ||
	( document.childNodes && !document.all && !navigator.taintEnabled && navigator.accentColorName); //https://phabricator.wikimedia.org/T21557
// For accesskeys; note that FF3+ is included here!
var is_ff2 = /firefox\/[2-9]|minefield\/3/.test( clientPC );
var is_ff2_ = /firefox\/2/.test( clientPC );
// These aren't used here, but some custom scripts rely on them
var is_ff2_win = is_ff2 && clientPC.indexOf('windows') != -1;
var is_ff2_x11 = is_ff2 && clientPC.indexOf('x11') != -1;
if (clientPC.indexOf('opera') != -1) {
	var is_opera = true;
	var is_opera_preseven = window.opera && !document.childNodes;
	var is_opera_seven = window.opera && document.childNodes;
	var is_opera_95 = /opera\/(9.[5-9]|[1-9][0-9])/.test( clientPC );
}
 
function importStylesheetURI(url) {
	$('head').append( $('<link rel="stylesheet" type="text/css" />').attr('href', url));
}
 

// special stylesheet links
if (!!mw.config.get('stylepath') && !!mw.config.get('skin')) {
	if (is_opera_preseven) {
		importStylesheetURI(mw.config.get('stylepath')+'/'+mw.config.get('skin')+'/scummmodern/Opera6Fixes.css');
	} else if (is_opera_seven && !is_opera_95) {
		importStylesheetURI(mw.config.get('stylepath')+'/'+mw.config.get('skin')+'/scummmodern/Opera7Fixes.css');
	} else if (is_opera_95) {
		importStylesheetURI(mw.config.get('stylepath')+'/'+mw.config.get('skin')+'/scummmodern/Opera9Fixes.css');
	} else if (is_khtml) {
		importStylesheetURI(mw.config.get('stylepath')+'/'+mw.config.get('skin')+'/scummmodern/KHTMLFixes.css');
	} else if (is_ff2_) {
		importStylesheetURI(mw.config.get('stylepath')+'/'+mw.config.get('skin')+'/scummmodern/FF2Fixes.css');
	}
}

