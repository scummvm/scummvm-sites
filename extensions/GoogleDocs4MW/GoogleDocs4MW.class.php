<?php
/**
 * GoogleDocs4MW parser extension - adds <googlespreadsheet> tag for displaying
 * Google Docs' spreadsheets
 *
 * @file
 * @ingroup Extensions
 * @version 1.2
 * @author Jack Phoenix <jack@shoutwiki.com>
 * @copyright © 2008-2015 Jack Phoenix
 * @license http://www.gnu.org/copyleft/gpl.html GNU General Public License 2.0 or later
 */

class GoogleDocs4MW {

	public static function registerTag( &$parser ) {
		$parser->setHook( 'googlespreadsheet', array( __CLASS__, 'renderGoogleSpreadsheet' ) );
		return true;
	}

	// The callback function for converting the input to HTML output
	public static function renderGoogleSpreadsheet( $input, $argv ) {
		$width = isset( $argv['width'] ) ? $argv['width'] : 500;
		$height = isset( $argv['height'] ) ? $argv['height'] : 300;
		$style = isset( $argv['style'] ) ? $argv['style'] : 'width:100%';
		$key = htmlspecialchars( $input, ENT_QUOTES );

		$output = '<iframe class="googlespreadsheetframe" width="' .
				intval( $width ) . '" height="' .
				intval( $height ) . '" style="' .
				htmlspecialchars( $style, ENT_QUOTES ) .
				'" src="http://spreadsheets.google.com/pub?key=' . $key .
				'&output=html&widget=true"></iframe>';

		return $output;
	}

}