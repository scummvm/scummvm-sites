<?php
# vim: ts=2 sw=2 expandtab
/**
 * http://www.mediawiki.org/wiki/Extension:MathJax
 * http://www.gnu.org/licenses/gpl-3.0.txt 
 *
 * @synopsis
 * Enables MathJax (http://www.mathjax.org/) for typesetting TeX and LaTeX 
 * formulae in MediaWiki inside $, \( and <math> (for inline) and $$, \[ and 
 * :<math> (for display) math environments. This gives nice and scalable 
 * mathematics. The extension also enables the usage of \label{} and \eqref{} 
 * tags with automatic formula numbering. If needed you can still hand label by 
 * using \tag{}.
 *
 * @note It doesn't matter if you have math support on or off in your MediaWiki 
 * installation, this extension strips the math tags before the standard math 
 * processor gets a chance to act.
 *
 * We use four hooks to make this work.
 *  1. We need to add the MathJax Javascript files to the header of the document.
 *     For that we use the "BeforePageDisplay" hook and use the addScript() 
 *     method of the OutputPage object. At the same time we load the MathJax 
 *     configuration hub from a user defined file.
 *  2. We preprocess the raw text content of the wiki page to detect, change and 
 *     protect the math environments. This is done in the "ParserBeforeStrip" 
 *     hook. In this hook we need to protect math environments occurring in 
 *     nowiki tags from being typeset, for that we wrap those inside 
 *     '<span class="tex2jax_ignore"> </span>'. 
 *     In a second stage parser, attached to the "InternalParseBeforeLinks" 
 *     hook, all math snippets are then removed and replaced by place holders 
 *     using the $parser->mStripList->nowiki ReplacementArray; they will be put 
 *     back in place by the standard unstripNoWiki call in Parser.php in the 
 *     function Parser::parse.
 *  3. Optionally: we want to change the edit toolbar to show two math buttons: 
 *     one for inline math and one for display math.
 *
 * @note The stripping is not done when we detect Semantic Media Wiki input 
 * fields (as they will stop working). In such a case we remove all annoying 
 * whitespace and assume the TeX formula will not break further processing.
 *
 * @author  Dirk Nuyens (dirk.nuyens at cs.kuleuven.be)
 * @date    Thu Feb  3 15:57:36 CET 2011
 * @version 0.5.2
 *
 * Changelog:
 *   0.5        Initial public release.
 *   0.5.1      Modifications to allow integration with Semantic MW  (SMW).
 *              Compatability code for Parser::MARKER_SUFFIX added.
 *   0.5.2      Kind of revert move away from the markers used by MW as it
 *              does no really matter which ones we use (so no need for the SMW 
 *              fix from 0.5.1 anymore).
 *              Allowed \label and \tag at the same time as one would expect.
 *              Added clickable links for the formula references, this currently 
 *              assumes the used label or tag is a valid XHTML id.
 */
 
# We can't run without MW:
if(!defined('MEDIAWIKI'))
  die('This is a mediawiki extensions and can\'t be run from the command line.');
 
# List the extension on the Special:Version page
$wgExtensionCredits['other'][] = array(
  'path'         => __FILE__,
  'name'         => 'MathJax',
  'version'      => '0.5.2',
  'author'       => array('Dirk Nuyens'),
  'url'          => 'http://www.mediawiki.org/wiki/Extension:MathJax',
  'description'  => 'Enables MathJax (http://www.mathjax.org/) for typesetting TeX '
                   .'and LaTeX formulae in MediaWiki inside <tt><nowiki>$</nowiki>'
                   .'</tt>, <tt>\(</tt> and <tt>&lt;math&gt;</tt> (for inline) and '
                   .'<tt><nowiki>$$</nowiki></tt>, <tt>\[</tt> and <tt>:&lt;math&gt;'
                   .'</tt> (for display) math environments.'
                   .' This gives nice and scalable mathematics. The extension also '
                   .'enables the usage of <tt>\label{}</tt> and <tt><nowiki>\eqref{}'
                   .'</nowiki></tt> tags with automatic formula numbering. If needed'
                   .' you can still hand label by using <tt>\tag{}</tt>.',
);
 
 
/**
 * MathJax_Javascript_addJS($out)
 *
 * Add the MathJax Javascript files to the header as well as the contents of the 
 * configuration hub file inside the script tags.
 *
 * This is controlled through the global associative array $wgMathJaxJS which 
 * could look like:
 * <code>
 *   $wgMathJaxJS = array(
 *     "/mathjax/MathJax.js" => "../mathjax/myMathJaxConfig.js"
 *   );
 * </code>
 * The keys are URL's, while the values are file paths. So for the example above 
 * the MathJax Javascript files are accessible on the webserver as 
 * http://WEBSERVER/mathjax/ and the configuration hub file is accessible as a 
 * file from within php using the path "../mathjax/myMathJaxConfig.js".
 * The URL for MathJax.js should best be a relative URL, see the installation 
 * manual of MathJax "Notes about shared installations", to avoid problems with 
 * counter measures for cross side scripting attacks (aka XSS attacks).
 *
 * @note We don't include the Javascript on Special pages, so there is no math 
 * rendering there. E.g., in Special:AllMessages there are occurrences of 
 * [[$1]][[$2]] which we don't want to typeset, and which don't pass through the 
 * parser.
 *
 * @param out   The OutputPage object being rendered (in nearly finished form).
 *
 * @returns     true on success; false on failure (never triggered).
 *
 * @hook        BeforePageDisplay
 * @globals     $wgMathJaxJS (associative array), $wgTitle, $wgJsMimeType
 */
$wgHooks['BeforePageDisplay'][] = 'MathJax_Javascript_addJS';
$wgMathJaxJS = array();
function MathJax_Javascript_addJS($out)
{
  global $wgTitle, $wgJsMimeType, $wgMathJaxJS;
  if($wgTitle->getNamespace() == NS_SPECIAL) {
    $out->addScript("<script type='$wgJsMimeType'>/* No MathJax: Special page */</script>\n");
    return true;
  }
  // In principle we can include any Javascript file from LocalSettings.php by 
  // abusing this script for other purposes. That is safe, as we have to assume 
  // LocalSettings.php is controlled by the sysadmin.
  foreach($wgMathJaxJS as $src => $inline) {
    $out->addScript("<script type='$wgJsMimeType' src='$src'>" . file_get_contents($inline) . "</script>\n");
  }
  return true;
}
 
/**
 * MathJax_change_edit_toolbar(&$toolbar)
 *
 * Remove the standard math button from the toolbar and add two new ones for 
 * inline style and for display style mathematics.
 *
 * Through the globals $wgMathJaxInlineButton, $wgMathJaxDisplayButton one can 
 * specify a file path to an image file to use for the button. If empty, then 
 * the standard math button is used for both buttons.
 *
 * @note This code will break whenever the toolbar code changes its output 
 * format. We can't help that, that's because there is no nice interface to do 
 * this.
 * @note On Wikipedia there is already a different toolbar in use, but without 
 * math button, so in that case, it doesn't matter much.
 *
 * @param $toolbar    This is the "HTML" rendered version of the edit toolbar, 
 *                    using Javascript calls "addButton()" to add buttons.
 *
 * @returns     true on success; false on failure (never triggered).
 *
 * @hook        EditPageBeforeEditToolbar
 * @globals     $wgMathJaxInlineButton, $wgMathJaxDisplayButton, $wgStylePath
 */
$wgHooks['EditPageBeforeEditToolbar'][] = 'MathJax_change_edit_toolbar';
function MathJax_change_edit_toolbar(&$toolbar)
{
  global $wgMathJaxInlineButton, $wgMathJaxDisplayButton, $wgStylePath;
  $i = strpos($toolbar, 'mw-editbutton-math');
  if($i === false)
    return true; // don't do anything, we can't find the math button...
  $e = strpos ($toolbar, ';', $i);
  $b = strrpos(substr($toolbar, 0, $e), 'addButton');
  $l = $e - $b + 2;
  if(empty($wgMathJaxInlineButton))
    $wgMathJaxInlineButton = "$wgStylePath/common/images/button_math.png";
  if(empty($wgMathJaxDisplayButton))
    $wgMathJaxDisplayButton = "$wgStylePath/common/images/button_math.png";
  $inline_math = 'addButton("' . $wgMathJaxInlineButton . '"'
    . ',"Inline mathematical formula (LaTeX)","$","$","Insert formula here","mw-editbutton-math");' . "\n";
  $display_math = 'addButton("'. $wgMathJaxDisplayButton . '"'
    . ',"Display-style mathematical formula (LaTeX)","$$","$$",'
    . '"Insert formula here, optionally \\\\tag{manual-number}","mw-editbutton-math2");' . "\n";
  $toolbar = substr_replace($toolbar, $inline_math . $display_math, $b, $l);
  return true;
}
 
/**
 * MathJax_parser_stage1(&$parser, &$text, &$strip_state)
 *
 * Preprocess the raw wiki text (we have hooked this early on in the processing 
 * chain) for mathematics. This means we have to:
 *
 *   1. Prevent math environments inside "<nowiki>...</nowiki>", 
 *      "<pre>...</pre>" and "<code>...</code>" from being typeset on the final 
 *      page. The pre and code tags are special: we can not just block them in 
 *      the MathJax configuration hub as WM may add them as markup to other 
 *      elements.
 *      These tags (nowiki, pre and code) will not be handled correctly for 
 *      template expansions, as their is no ParserBeforeStrip stage for 
 *      templates.
 *      For template arguments using these tags there is no problem at all.
 *   2. Change the standard "<math>...</math>" tag into MathJax delimiters for 
 *      inline style math.
 *   3. Change the ":<math>...</math>" combination (as used on Wikipedia for 
 *      display style math)  into MathJax delimiters for display style math.
 *   4. Protect our math environments from further processing by putting in 
 *      place holders; we use the $strip_state->nowiki ReplacementArray for 
 *      this. These place holders will be automatically unstripped by 
 *      unstripNoWiki in Parser::Parse just before the ParserBeforeTidy hook.
 *
 * There is a stage 2 parser which will replace the actual math by place holders 
 * and does the \label{} and \eqref{} handling. This stage 2 parser will also 
 * see the expanded templates; and therefore, there as well, we will replace 
 * "<math>...</math>" and ":<math>...</math>" by MathJax delimiters.
 *
 * @note Partly based on code from Extension:JsMath by Tommy Ekola. Maybe the 
 * WikiMedia developers should document their code base a little bit more... 
 * Luckily examples (like Extension:JsMath) and source code reading helps.
 *
 * @param &$parser        The Parser object doing the job.
 * @param &$text          The raw wiki text which is thrown in.
 * @param &$strip_state   A StripState object which holds two 
 *                        ReplacementArray's which are key value lists of place 
 *                        holders (substituted into the $text) and their value.
 *
 * @returns               true on success; false on failure (never triggered).
 *
 * @hook        ParserBeforeStrip
 * @globals
 * @seealso     MathJax_parser_stage2
 */
$wgHooks['ParserBeforeStrip'][] = 'MathJax_parser_stage1';
function MathJax_parser_stage1(&$parser, &$text, &$strip_state)
{
  $uniq_prefix = substr($parser->mUniqPrefix, 1);
  $tempstrip = new ReplacementArray;
  $elements = array('nowiki', 'pre', 'code'); // pre and code are handled differently in wiki than in html
  $matches = array();
  $nowiki_markers_replace = array();
  $precode_markers_replace = array();
  $text = Parser::extractTagsAndParams($elements, $text, $matches, $uniq_prefix);
  foreach($matches as $marker => $data) {
    list($element, $content, $params, $tag) = $data;
    $tagName = strtolower($element);
    switch($tagName) {
    case '!--': // Comment <!-- ... --> gets always extracted
      $output = $tag;
      $tempstrip->setPair($marker, $output);
      break;
    case 'nowiki': // <nowiki> ... </nowiki>
      $output = $tag;
      // we add the spans after this loop
      $nowiki_markers_replace[$marker]  = '<span class="tex2jax_ignore">' . $marker . '</span>';
      $strip_state->nowiki->setPair($marker, $output); // this will be "unstripped" in the normal code
      break;
    case 'pre':
    case 'code': // <pre> ... </pre> and <code> ... </code>
      $output = $tag;
      // we add the spans after this loop
      $precode_markers_replace[$marker]  = '<span class="tex2jax_ignore">' . $marker . '</span>';
      $tempstrip->setPair($marker, $output); // this will be "unstripped" in the normal code
      break;
    }
  }
  MathJax_subst_math_tag($text); // <math>...</math>
  // now add the spans for the nowiki parts by replacing the markers by spanned markers
  $text = strtr($text, $nowiki_markers_replace);
  // now add the spans for the pre and code parts by replacing the markers by spanned markers
  $text = strtr($text, $precode_markers_replace);
  // now it should be safe for our mathematics handling
  // but we delay that for the InternalParseBeforeLinks hook 
  // (MathJax_parser_stage2) as then templates have been expanded as well; note 
  // that the handling of nowiki, pre and code will be messed up for templates!
  #MathJax_parser_stage2($parser, $text, $strip_state);
  // Insert the comments back in: Unstrip comments, pre and code
  $text = $tempstrip->replace($text);
  return true;
}
 
/**
 * MathJax_parser_stage2(&$parser, &$text, &$strip_state)
 *
 * The stage 2 math parser will "strip" (replace by place holders) all math 
 * environments, adding them to the $strip_state->nowiki ReplacementArray.
 * Additionally we register the \label{}, if present, of the math environment and 
 * replace it by an auto numbered \tag{} and then replace all occurrences of 
 * \eqref{} by the correct formula number. Existing \tag{} commands are also 
 * registered such that they can be referenced using \eqref{}.
 *
 * The stage 2 parser will see the expanded templates; and therefore, here as 
 * well, we will replace "<math>...</math>" and ":<math>...</math>" by MathJax 
 * delimiters. We can not handle nowiki, pre and code tags in the expanded 
 * templates.
 *
 * @param &$parser        The Parser object doing the job.
 * @param &$text          The text which is thrown in.
 * @param &$strip_state   A StripState object which holds two 
 *                        ReplacementArray's which are key value lists of place 
 *                        holders (substituted into the $text) and their value.
 *
 * @returns               true on success; false on failure (never triggered).
 *
 * @hook        InternalParseBeforeLinks
 * @globals     $MathJax_strip_state, $MathJax_unique_prefix, $MathJax_mark_n, $MathJax_marker_suffix
 *              $MathJax_eqnumber, $MathJax_eqnumbers
 * @seealso     MathJax_parser_stage1
 */
$MathJax_strip_state = null;
$MathJax_unique_prefix = null;
$MathJax_mark_n = 1;
$MathJax_eqnumber = 1;
$MathJax_eqnumbers = array();
$wgHooks['InternalParseBeforeLinks'][] = 'MathJax_parser_stage2';
function MathJax_parser_stage2(&$parser, &$text, &$strip_state)
{
  global $MathJax_strip_state, $MathJax_unique_prefix, $MathJax_marker_suffix, $MathJax_strip_ws_no_strip;
 
  // we need to add the formulas in a regex callback to the strip state
  // simple and dirty solution: use globals
  $MathJax_strip_state = $strip_state; // this is $parser->mStripState
  $MathJax_unique_prefix = substr($parser->uniqPrefix(), 1);
  // actually it doesn't matter much for our usage what the suffix is, but we 
  // try to use the one that is used in the rest of the MW code:
  // (code from the StringFunctions extension by Ross McClure & Juraj Simlovic)
  /*
  if(defined('Parser::MARKER_SUFFIX')) {
    $MathJax_marker_suffix = Parser::MARKER_SUFFIX;
  } elseif(isset($parser->mMarkerSuffix)) {
    $MathJax_marker_suffix = $parser->mMarkerSuffix;
  } elseif(defined('MW_PARSER_VERSION') && strcmp(MW_PARSER_VERSION, '1.6.1') > 0) {
    $MathJax_marker_suffix = "QINU\x07";
  } else {
    $MathJax_marker_suffix = 'QINU';
  }
  */
  $MathJax_marker_suffix = 'QINU';
 
  MathJax_subst_math_tag($text); // <math>...</math>
 
  // If $text contains Semantic MediaWiki markup then we are not going to 
  // "strip" as SMW will refuse fields with place holders.
  // In that case we will just clean up the math environment by removing all 
  // possible whitespace (such that doBlocks will not add <p> and <pre> 
  // elements) and the math will still stay in tact.
  // This should not really be a problem, but technically it could mess up 
  // further parsing? (Depending on how the TeX looks like.)
  // But also here the TeX should then not contain anything which looks like a 
  // SMW property (i.e., of the form "[[property name:property value]]").
  $semanticLinkPattern = '/\[\[                 # Beginning of the link
                          (?:([^:][^]]*):[=:])+ # Property name (or a list of those)
                          ([^\[\]]*)            # content: anything but [, |, ]
                          \]\]                  # End of link
                          /xu';
  #if(preg_match($semanticLinkPattern, $text)) $MathJax_strip_ws_no_strip = true;
  #else $MathJax_strip_ws_no_strip = false;

  // now handle all MathJax math environments by registering equations 
  // (numbering) and stripping them (replacing by place holder);
  // they get added to the nowiki strip list and will be unstripped in 
  // Parser::Parse just before the ParserBeforeTidy hook
  $text = preg_replace_callback('/(\\\\begin{(.*?)})(.*?)(\\\\end{\\2})/s', 'MathJax_register_and_strip_math', $text);
  // watch out for \$ in TeX using negative look behind:
  $text = preg_replace_callback('/((\${1,2}))(.*?)((?<!\\\\)\\2)/s', 'MathJax_register_and_strip_math', $text);
  $text = preg_replace_callback('/((\\\\\\[))(.*?)(\\\\\\])/s', 'MathJax_register_and_strip_math', $text);
  $text = preg_replace_callback('/((\\\\\\())(.*?)(\\\\\\))/s', 'MathJax_register_and_strip_math', $text);
 
  // replace all occurrences of \eqref{} (and also \ref{}) by the correct formula 
  // reference (as plain text, e.g., \eqref{sum} becomes (2))
  $text = preg_replace_callback('(\\\\(eq)?ref\\{(.*?)\\})', 'MathJax_replace_eqrefs', $text);
 
  return true;
}
 
/**
 * MathJax_subst_math_tag(&$text)
 *
 * Change "<math>...</math>"   into "\(...\)" (inline math style)
 *    and ":</math>...</math>" into "\[...\]" (display math style) in place.
 */
function MathJax_subst_math_tag(&$text)
{
  // Change <math>...</math> and :<math>...</math> into \(...\) and \[...\]
  $text = preg_replace('|:<math>(.*?)</math>|s', '\\\\[$1\\\\]', $text);
  $text = preg_replace('|<math>(.*?)</math>|s', '\\\\($1\\\\)', $text);
}
 
/**
 * MathJax_register_and_strip_math($matches)
 *
 * This is a regex callback used from MathJax_parser_stage2 to replace MathJax 
 * math environments and register an equation number (if \label{} or \tag{} is 
 * present).
 *
 * @param matches   Match array where 
 *                    $matches[1] is the opening math delimiter
 *                    $matches[3] is the TeX content
 *                    $matches[4] is the closing math delimiter
 *                  Note: $matches[2] has no function; it was used as a backref
 *
 * @return The marker which was used to replace the math environment.
 *
 * @globals   $MathJax_strip_state, $MathJax_unique_prefix, $MathJax_mark_n, $MathJax_marker_suffix
 *            $MathJax_eqnumber, $MathJax_eqnumbers, $MathJax_strip_ws_no_strip, $MathJax_remembered_label,
 *            $MathJax_label
 */
function MathJax_register_and_strip_math($matches)
{
  global $MathJax_strip_state, $MathJax_unique_prefix, $MathJax_mark_n, $MathJax_marker_suffix;
  global $MathJax_strip_ws_no_strip;
  global $MathJax_remembered_label, $MathJax_label;
  $eq = $matches[3];
  if($MathJax_strip_ws_no_strip) {
    $eq = preg_replace('/\n\s+/m', "\n", $eq); # remove initial whitespace on a line
    $eq = preg_replace('/^$/s', '', $eq);      # remove empty lines
    $eq = preg_replace('/\s+\n/', "\n", $eq);  # remove whitespace at end of lines
    $eq = preg_replace('/\n/', " ", $eq);      # and now also put everything on one line
  }
  // formula numbering
  $MathJax_label = false; // to remember if we had to label
  // first check if there is a \label and a \tag
  $MathJax_remembered_label = "";
  if((strpos($eq, '\\tag') !== false) && preg_match('/\\\\label\{(.*?)\}/', $eq, $matches2)) {
    // if so then remove the label and remember it
    $MathJax_remembered_label = $matches2[1];
    $eq = str_replace('\\label{'.$matches2[1].'}', '', $eq);
  }
  // formula numbering
  $eq = preg_replace_callback('(\\\\(label|tag)\{(.*?)\})', 'MathJax_register_eq', $eq);
  $stripped = $matches[1] . $eq . $matches[4];
  if($MathJax_label) $stripped = '<span id="Eq-' . $MathJax_label . '"/>' . $stripped;
  if(!$MathJax_strip_ws_no_strip) {
    $marker = $MathJax_unique_prefix . "-MathJax-" . sprintf('%08X', $MathJax_mark_n++) . $MathJax_marker_suffix;
    $MathJax_strip_state->nowiki->setPair($marker, $stripped);
    return $marker;
  } else {
    return $stripped;
  }
}
 
/**
 * MathJax_register_eq($matches)
 *
 * This is a regex callback used from MathJax_register_and_strip_math to 
 * register a formula number (or given tag) for later referencing by \eqref.
 *
 * @param matches   Match array where
 *                    $matches[1]   is either 'label' or 'tag'
 *                    $matches[2]   is the argument from \label{} or \tag{}
 *
 * @return An autonumbered tag.
 *
 * @globals   $MathJax_eqnumber, $MathJax_eqnumbers, $MathJax_remembered_label, $MathJax_label
 */
function MathJax_register_eq($matches)
{
  global $MathJax_eqnumber, $MathJax_eqnumbers, $MathJax_remembered_label, $MathJax_label;
  $label = $matches[2];
  if(array_key_exists($label, $MathJax_eqnumbers) or 
    ($MathJax_remembered_label and array_key_exists($MathJax_remembered_label, $MathJax_eqnumbers))) 
    return '\\tag{' . $label . ':label exists!}';
  $MathJax_eqnumbers[$label] = $matches[1] == 'label' ? $MathJax_eqnumber++ : $label;
  $MathJax_label = $MathJax_eqnumbers[$label];
  if($MathJax_remembered_label) $MathJax_eqnumbers[$MathJax_remembered_label] = $MathJax_eqnumbers[$label];
  return '\\tag{' . $MathJax_eqnumbers[$label] . '}';
}
 
/**
 * MathJax_replace_eqrefs($matches)
 *
 * This is a regex callback used from MathJax_parser_stage2 to replace all 
 * \eqref{} references with the correct formula reference.
 *
 * @param matches   Match array where
 *                    $matches[2]   is the argument of \eqref{}
 *
 * @return A clickable reference.
 *
 * @globals   $MathJax_eqnumbers
 */
function MathJax_replace_eqrefs($matches)
{
  global $MathJax_eqnumbers;
  $label = $matches[2]; # the possible "eq" for "eqref" is in $matches[1]...
  if(array_key_exists($label, $MathJax_eqnumbers)) 
    return '(<a href="#Eq-' . $MathJax_eqnumbers[$label] . '">' . $MathJax_eqnumbers[$label] . '</a>)';
  return "<span style='color: red;'>" . $matches[0] . "</span>";
}