<?php
/**
 * Skin file for the ScummModern skin.
 *
 * @file
 * @ingroup Skins
 */

/**
 * SkinTemplate class for the ScummModern skin
 *
 * @ingroup Skins
 */
class SkinScummModern extends SkinTemplate {
	public $skinname = 'scummmodern', $stylename = 'ScummModern',
		$template = 'ScummModernTemplate', $useHeadElement = true;

public function initPage( OutputPage $out ) {
		parent::initPage( $out );

		$out->addModules( array( 'skins.scummmodern.js' ) );
	}

	/**
	 * Add CSS via ResourceLoader
	 *
	 * @param $out OutputPage
	 */
	function setupSkinUserCss( OutputPage $out ) {
		parent::setupSkinUserCss( $out );
		$out->addModuleStyles( array(
			'mediawiki.skinning.interface', 'skins.scummmodern'
		) );
		//TODO: Figure out if these can be added to skin.json
		$out->addStyle( 'scummmodern/ie6.css', 'screen', 'IE 6' );
		$out->addStyle( 'scummmodern/ie7.css', 'screen', 'IE 7' );
	}
}

/**
 * BaseTemplate class for the Example skin
 *
 * @ingroup Skins
 */
class ScummModernTemplate extends BaseTemplate {
	/**
	 * Outputs a single sidebar portlet of any kind.
	 */
	private function outputPortlet( $box ) {
		if ( !$box['content'] ) {
			return;
		}

		?>
		<div
			role="navigation"
			class="mw-portlet"
			id="<?php echo Sanitizer::escapeId( $box['id'] ) ?>"
			<?php echo Linker::tooltip( $box['id'] ) ?>
		>
			<h3>
				<?php
				if ( isset( $box['headerMessage'] ) ) {
					$this->msg( $box['headerMessage'] );
				} else {
					echo htmlspecialchars( $box['header'] );
				}
				?>
			</h3>

			<?php
			if ( is_array( $box['content'] ) ) {
				echo '<ul>';
				foreach ( $box['content'] as $key => $item ) {
					echo $this->makeListItem( $key, $item );
				}
				echo '</ul>';
			} else {
				echo $box['content'];
			}?>
		</div>
		<?php
	}

	var $skin;
	/**
	 * Template filter callback for ScummVM skin.
	 * Takes an associative array of data set from a SkinTemplate-based
	 * class, and a wrapper for MediaWiki's localization database, and
	 * outputs a formatted page.
	 *
	 * @access private
	 */
	
	public $menuClassList = array("menu-main", "menu-misc", "menu-sf"); // What class
	public $menuClassCounter = 0; // This determines what img gets shown in the nav

	public $leftTabs = array("nstab-main", "talk"); //This is what tabs are on the left, the rest are on the right

	function menuClass() {

		if($this->menuClassCounter > count($this->menuClassList)-1) {

			$this->menuClassCounter = 0; // start again
		}
		$returnVal = $this->menuClassList[$this->menuClassCounter];
		$this->menuClassCounter++;
		echo $returnVal;
	}

	function execute() {
		global $wgRequest;
		$this->skin = $skin = $this->data['skin'];
		$action = $wgRequest->getText( 'action' );

		// Suppress warnings to prevent notices about missing indexes in $this->data
		wfSuppressWarnings();

?>
<?php $this->html('headelement'); ?>

<?php wfRunHooks( 'MakeGlobalVariablesScript', array( $this->data ) ); ?>

<body<?php if($this->data['body_ondblclick']) { ?> ondblclick="<?php $this->text('body_ondblclick') ?>"<?php } ?>
<?php if($this->data['body_onload']) { ?> onload="<?php $this->text('body_onload') ?>"<?php } ?>
 class="mediawiki <?php $this->text('dir') ?> <?php $this->text('pageclass') ?> <?php $this->text('skinnameclass') ?>">
	
<table width="90%" border="0" cellspacing="0" cellpadding="0" align="center" id="tableMain">
  <tr id="topHeader"> 
    <td width="199px"><a href="<?php echo htmlspecialchars($this->data['nav_urls']['mainpage']['href'])?>"<?php
			echo $skin->tooltipAndAccesskeyAttribs('p-logo') ?>><img src="<?php echo htmlspecialchars( $this->getSkin()->getSkinStylePath( 'scummmodern/logo_phpVB2.png'));?>" width="199" height="65" alt="ScummVM logo" /></a></td>

    <td width="50%" style="background-image: url('<?php echo htmlspecialchars( $this->getSkin()->getSkinStylePath( 'scummmodern/top_bg.png')); ?>'); vertical-align: middle; text-align: left; white-space:nowrap;">
      <a href="http://www.scummvm.org/" target="_parent" class="toplinks" id="tl_mw">Main website</a> - 
      <a href="http://forums.scummvm.org/" target="_parent" class="toplinks" id="tl_f">Forums</a> -
      <a href="http://buildbot.scummvm.org" target="_parent" class="toplinks" id="tl_b">BuildBot</a> -
      <a href="http://doxygen.scummvm.org" target="_parent" class="toplinks" id="tl_d">Doxygen</a> -
      <a href="http://planet.scummvm.org" target="_parent" class="toplinks" id="tl_p">Planet</a> <br />
      <a href="http://www.scummvm.org/contact.php" target="_parent" class="toplinks" id="tl_cu">Contact us</a> -
      Buy Supported Games: <b><a href="http://www.gog.com/?pp=22d200f8670dbdb3e253a90eee5098477c95c23d" target="_parent" class="toplinks" id="tl_go">GOG.com</a></b>
	  </td>
	
	  <td width="50%" style="background-image: url('<?php echo htmlspecialchars( $this->getSkin()->getSkinStylePath( 'scummmodern/top_bg.png')); ?>'); vertical-align: middle; text-align: right; white-space:nowrap;">
      <!-- new nav table -->
      <?php $num_p_urls = count($this->data['personal_urls']); $num_p_urls_count = 0;
	foreach($this->data['personal_urls'] as $key => $item) {
		if ($num_p_urls_count != 0) { 
			if ($num_p_urls_count != round($num_p_urls/2)) {	
		?> - <?php
		} }		
		if ($num_p_urls_count == round($num_p_urls/2)) { ?> <br /> <?php } // end if <= 	
		$num_p_urls_count++;		
 	?>
				<a href="<?php echo htmlspecialchars($item['href']) ?>" class="toplinks">
        <?php echo htmlspecialchars($item['text']) ?></a> 
      <?php		} //end for each ?>
    </td>
    <td><img src="<?php echo htmlspecialchars( $this->getSkin()->getSkinStylePath( 'scummmodern/curve_tr.png'));?> width="20" height="65" alt="curved edge" /></td>
  </tr>
  <!-- top logo, navbar ends here, now on to the main forum body -->
  <tr id="tableColor" bgcolor="#fbf1ce"> 
    <td colspan="4">
      <table width="100%" border="0" cellspacing="0" cellpadding="0" style="padding-left: 5px; padding-right: 5px;">
        <tr>
          <td>
	          <div id="container"> 
  	          <a name="top" id="top"></a>
  				      <div id="menu"> <!-- start of menu -->
  	             <script type="<?php $this->text('jsmimetype') ?>"> if (window.isMSIE55) fixalpha(); </script>
                 <?php
  		           $sidebar = $this->data['sidebar'];
  		           if ( !isset( $sidebar['SEARCH'] ) ) $sidebar['SEARCH'] = true;
  		           if ( !isset( $sidebar['TOOLBOX'] ) ) $sidebar['TOOLBOX'] = true;
  		           if ( !isset( $sidebar['LANGUAGES'] ) ) $sidebar['LANGUAGES'] = true;
  		           foreach ($sidebar as $boxName => $cont) {
  			           if ( $boxName == 'SEARCH' ) {
  				         $this->searchBox();
  			           } elseif ( $boxName == 'TOOLBOX' ) {
  				         $this->toolbox();
  			           } elseif ( $boxName == 'LANGUAGES' ) {
  				         $this->languageBox();
  			           } else {
  				         $this->customBox( $boxName, $cont );
  			           }
  		           }





                 ?>	
                </div><!-- end of menu -->
  		        <?php if($this->data['sitenotice']) { ?><div id="siteNotice"><?php $this->html('sitenotice') ?></div><?php } ?>
  
  	          <div id="p-cactions" class="portlet">
            		<div class="tabs"><!-- start of Views -->
  			         <div id="ltabs"><ul>
  	               <?php		//this is view source and edit etc
                   foreach($this->data['content_actions'] as $key => $tab) {
  					         if(in_array($key,$this->leftTabs)){ echo '<li id="' . Sanitizer::escapeId( "ca-$key" ) . '"';
            				 if( $tab['class'] ) {
            					echo ' class="'.htmlspecialchars($tab['class']).'"';
            				 }
  					         echo'><a href="'.htmlspecialchars($tab['href']).'"';
            				 # We don't want to give the watch tab an accesskey if the
            				 # page is being edited, because that conflicts with the
            				 # accesskey on the watch checkbox.  We also don't want to
            				 # give the edit tab an accesskey, because that's fairly su-
            				 # perfluous and conflicts with an accesskey (Ctrl-E) often
            				 # used for editing in Safari.
            				 if( in_array( $action, array( 'edit', 'submit' ) ) && in_array( $key, array( 'edit', 'watch', 'unwatch' ))) {
  				 	          echo $skin->tooltip( "ca-$key" );
  				 	         } else {
  				 		        echo $skin->tooltipAndAccesskeyAttribs( "ca-$key" );
  				 	         }
  				 	         if( $tab['class'] ) {
  						        echo ' class="'.htmlspecialchars($tab['class']).'"';
  					         }
                     echo '><span>'.htmlspecialchars($tab['text']).'</span></a></li>';
  				         }} ?>
  			         </ul></div>
  			         <div id="rtabs"><ul>
  	               <?php		//this is view source and edit etc
                   foreach($this->data['content_actions'] as $key => $tab) {
  					         if(!in_array($key,$this->leftTabs)){echo '<li id="' . Sanitizer::escapeId( "ca-$key" ) . '"';
            				 if( $tab['class'] ) {
            					echo ' class="'.htmlspecialchars($tab['class']).'"';
            				 }
  					         echo'><a href="'.htmlspecialchars($tab['href']).'"';
            				 # We don't want to give the watch tab an accesskey if the
            				 # page is being edited, because that conflicts with the
            				 # accesskey on the watch checkbox.  We also don't want to
            				 # give the edit tab an accesskey, because that's fairly su-
            				 # perfluous and conflicts with an accesskey (Ctrl-E) often
            				 # used for editing in Safari.
            				 if( in_array( $action, array( 'edit', 'submit' ) ) && in_array( $key, array( 'edit', 'watch', 'unwatch' ))) {
  				 	          echo $skin->tooltip( "ca-$key" );
  				 	         } else {
  				 		        echo $skin->tooltipAndAccesskeyAttribs( "ca-$key" );
  				 	         }
  				 	         if( $tab['class'] ) {
  						        echo ' class="'.htmlspecialchars($tab['class']).'"';
  					         }
                     echo '><span>'.htmlspecialchars($tab['text']).'</span></a></li>';
  				         }} ?>
  			         </ul></div>
  		          </div> <!-- end of Views -->
  	          </div>
  		        <div class="rbtop"> <!-- start of title -->
			         <div>
				        <p><span class="shadow-container" style="color: #fff;"><?php $this->data['displaytitle']!=""?$this->html('title'):$this->text('title') ?><span class="shadow-text" style="color: #821d06;"><?php $this->data['displaytitle']!=""?$this->html('title'):$this->text('title') ?></span></span><br /></p>
               </div>
              </div> <!-- end of title -->
		          <div class="rbcontent">
			         <div class="rbwrapper">
		            <div id="bodyContent">
			           <div id="contentSub"><?php $this->html('subtitle') ?></div>
			           <?php if($this->data['undelete']) { ?><div id="contentSub2"><?php     $this->html('undelete') ?></div><?php } ?>
          			 <?php if($this->data['newtalk'] ) { ?><div class="usermessage"><?php $this->html('newtalk')  ?></div><?php } ?>
          			 <!-- start content -->
          			 <?php $this->html('bodytext') ?>
          			 <?php if($this->data['catlinks']) { $this->html('catlinks'); } ?>
          			 <!-- end content -->
          			 <?php if($this->data['dataAfterContent']) { $this->html ('dataAfterContent'); } ?>
          			 <div class="visualClear"></div>
		            </div>
             	 </div>
		          </div>

<div class="rbbot"><div><p>&nbsp;</p></div></div> 
      <div class="visualClear"></div>
			<div id="footer">
<?php
		if($this->data['poweredbyico']) { ?>
				<div id="f-poweredbyico"><?php $this->html('poweredbyico') ?></div>
<?php 	}
		if($this->data['copyrightico']) { ?>
				<div id="f-copyrightico"><?php $this->html('copyrightico') ?></div>
<?php	}

		// Generate additional footer links
		$footerlinks = array(
			'lastmod', 'viewcount', 'numberofwatchingusers', 'credits', 'copyright',
			'privacy', 'about', 'disclaimer', 'tagline',
		);
		$validFooterLinks = array();
		foreach( $footerlinks as $aLink ) {
			if( isset( $this->data[$aLink] ) && $this->data[$aLink] ) {
				$validFooterLinks[] = $aLink;
			}
		}
		if ( count( $validFooterLinks ) > 0 ) {
?>			<ul id="f-list">
<?php
			foreach( $validFooterLinks as $aLink ) {
				if( isset( $this->data[$aLink] ) && $this->data[$aLink] ) { 
?>					<li id="<?php echo$aLink?>"><?php $this->html($aLink) ?></li>
<?php 			}
			}
?>
			</ul>
<?php	}
?>
		</div>
</div>
<?php $this->html('bottomscripts'); /* JS call to runBodyOnloadHook */ ?>
<?php $this->html('reporttime') ?>
<?php if ( $this->data['debug'] ): ?>
<!-- Debug output:
<?php $this->text( 'debug' ); ?>

-->
<?php endif; ?>
	</div>

</td>
        </tr>
      </table>
    </td>
  </tr>
  <tr> 
    <td colspan="4">
      <table width="100%" border="0" cellspacing="0" cellpadding="0" id="tableFooter">
        <tr>
          <td><img src="<?php echo htmlspecialchars( $this->getSkin()->getSkinStylePath( 'scummmodern/curve_bl.png'));?> width="20" height="20" alt="curved edge" /></td>

          <td width="100%" bgcolor="#fbf1ce">&nbsp;</td>
          <td align="right" valign="bottom"><img src="<?php echo htmlspecialchars( $this->getSkin()->getSkinStylePath( 'scummmodern/curve_br.png'));?> width="20" height="20" alt="curved edge" /></td>
        </tr>
      </table>
    </td>
  </tr>
</table>
</div>
</body>
</html>
<?php
	wfRestoreWarnings();
	} // end of execute() method

	function searchBox() {
		global $wgUseTwoButtonsSearchForm;
?>
  <div class="menugroup">
		<h1 class="<?php $this->menuClass(); ?>" ><label for="searchInput"><?php $this->msg('search') ?></label></h1>
		<div id="searchBody" class="pBody" style="text-align: center;">
			<form action="<?php $this->text('wgScript') ?>" id="searchform">
				<input type='hidden' name="title" value="<?php $this->text('searchtitle') ?>"/>
				<input id="searchInput" name="search" type="text"<?php echo $this->skin->tooltipAndAccesskeyAttribs('search');
					if( isset( $this->data['search'] ) ) {
						?> value="<?php $this->text('search') ?>"<?php } ?> />
				<br /><input type='submit' name="go" class="searchButton" id="searchGoButton"	value="<?php $this->msg('searcharticle') ?>"<?php echo $this->skin->tooltipAndAccesskeyAttribs( 'search-go' ); ?> /><?php if ($wgUseTwoButtonsSearchForm) { ?>&nbsp;
				<input type='submit' name="fulltext" class="searchButton" id="mw-searchButton" value="<?php $this->msg('searchbutton') ?>"<?php echo $this->skin->tooltipAndAccesskeyAttribs( 'search-fulltext' ); ?> /><?php } else { ?>

				<div><a href="<?php $this->text('searchaction') ?>" rel="search"><?php $this->msg('powersearch-legend') ?></a></div><?php } ?>

			</form>
		</div>
	</div>
<?php
	}

	/*************************************************************************************************/
	function toolbox() {
?>
	<div class="menugroup">
		<h1 class="<?php $this->menuClass(); ?>"><?php $this->msg('toolbox') ?></h1>
		<div class="pBody">
			<ul>
<?php
		if($this->data['notspecialpage']) { ?>
				<li id="t-whatlinkshere"><a href="<?php
				echo htmlspecialchars($this->data['nav_urls']['whatlinkshere']['href'])
				?>"<?php echo $this->skin->tooltipAndAccesskeyAttribs('t-whatlinkshere') ?>><?php $this->msg('whatlinkshere') ?></a></li>
<?php
			if( $this->data['nav_urls']['recentchangeslinked'] ) { ?>
				<li id="t-recentchangeslinked"><a href="<?php
				echo htmlspecialchars($this->data['nav_urls']['recentchangeslinked']['href'])
				?>"<?php echo $this->skin->tooltipAndAccesskeyAttribs('t-recentchangeslinked') ?>><?php $this->msg('recentchangeslinked') ?></a></li>
<?php 		}
		}
		if(isset($this->data['nav_urls']['trackbacklink'])) { ?>
			<li id="t-trackbacklink"><a href="<?php
				echo htmlspecialchars($this->data['nav_urls']['trackbacklink']['href'])
				?>"<?php echo $this->skin->tooltipAndAccesskeyAttribs('t-trackbacklink') ?>><?php $this->msg('trackbacklink') ?></a></li>
<?php 	}
		if($this->data['feeds']) { ?>
			<li id="feedlinks"><?php foreach($this->data['feeds'] as $key => $feed) {
					?><a id="<?php echo Sanitizer::escapeId( "feed-$key" ) ?>" href="<?php
					echo htmlspecialchars($feed['href']) ?>" rel="alternate" type="application/<?php echo $key ?>+xml" class="feedlink"<?php echo $this->skin->tooltipAndAccesskeyAttribs('feed-'.$key) ?>><?php echo htmlspecialchars($feed['text'])?></a>&nbsp;
					<?php } ?></li><?php
		}

		foreach( array('contributions', 'log', 'blockip', 'emailuser', 'upload', 'specialpages') as $special ) {

			if($this->data['nav_urls'][$special]) {
				?><li id="t-<?php echo $special ?>"><a href="<?php echo htmlspecialchars($this->data['nav_urls'][$special]['href'])
				?>"<?php echo $this->skin->tooltipAndAccesskeyAttribs('t-'.$special) ?>><?php $this->msg($special) ?></a></li>
<?php		}
		}

		if(!empty($this->data['nav_urls']['print']['href'])) { ?>
				<li id="t-print"><a href="<?php echo htmlspecialchars($this->data['nav_urls']['print']['href'])
				?>" rel="alternate"<?php echo $this->skin->tooltipAndAccesskeyAttribs('t-print') ?>><?php $this->msg('printableversion') ?></a></li><?php
		}

		if(!empty($this->data['nav_urls']['permalink']['href'])) { ?>
				<li id="t-permalink"><a href="<?php echo htmlspecialchars($this->data['nav_urls']['permalink']['href'])
				?>"<?php echo $this->skin->tooltipAndAccesskeyAttribs('t-permalink') ?>><?php $this->msg('permalink') ?></a></li><?php
		} elseif ($this->data['nav_urls']['permalink']['href'] === '') { ?>
				<li id="t-ispermalink"<?php echo $this->skin->tooltip('t-ispermalink') ?>><?php $this->msg('permalink') ?></li><?php
		}

		wfRunHooks( 'ScummVMTemplateToolboxEnd', array( &$this ) );
		wfRunHooks( 'SkinTemplateToolboxEnd', array( &$this ) );
?>
			</ul>
		</div>
	</div>
<div><img src="<?php echo htmlspecialchars( $this->getSkin()->getSkinStylePath( 'scummmodern/hangmonk.gif')); ?>" alt="monkey" width="55" height="57" class="monkey float_right" /></div>
	<div id="menu_banners">
				<a href="http://sourceforge.net/donate/index.php?group_id=37116">
					<img src="http://images.sourceforge.net/images/project-support.jpg" width="88" height="32" alt="Support This Project" />
				</a>	
				<a href="http://combobreaker.com/">
					<img src="<?php echo htmlspecialchars( $this->getSkin()->getSkinStylePath( 'scummmodern/scummvm_cb.png')); ?>" alt="Combobreaker.com T-Shirts" width="88" height="32" />
				</a>
				<a href="http://www.gog.com/?pp=22d200f8670dbdb3e253a90eee5098477c95c23d">
					<img src="<?php echo htmlspecialchars( $this->getSkin()->getSkinStylePath( 'scummmodern/GOG_button_small.png' ) ); ?>" alt="Buy with GOG.com" width="88" height="32" />
				</a>
			</div>
			<?php
	}

	/*************************************************************************************************/
	function languageBox() {
		if( $this->data['language_urls'] ) {
?>
	<div id="menugroup" class="portlet">
		<h1 class="<?php $this->menuClass(); ?>"><?php $this->msg('otherlanguages') ?></h1>
		<div class="pBody">
			<ul>
<?php		foreach($this->data['language_urls'] as $langlink) { ?>
				<li class="<?php echo htmlspecialchars($langlink['class'])?>"><?php
				?><a href="<?php echo htmlspecialchars($langlink['href']) ?>"><?php echo $langlink['text'] ?></a></li>
<?php		} ?>
			</ul>
		</div>
	</div>
<?php
		}
	}

	/*************************************************************************************************/
	function customBox( $bar, $cont ) {
?>
	<div class='menugroup' id='<?php echo Sanitizer::escapeId( "p-$bar" ) ?>'<?php echo $this->skin->tooltip($bar) ?>>
		<h1 class="<?php $this->menuClass(); ?>"><?php $out = wfMsg( $bar ); if (wfEmptyMsg($bar, $out)) echo $bar; else echo $out; ?></h1>
		<div class='pBody'>
<?php   if ( is_array( $cont ) ) { ?>
			<ul>
<?php 			foreach($cont as $key => $val) { ?>
				<li id="<?php echo Sanitizer::escapeId($val['id']) ?>"<?php
					if ( $val['active'] ) { ?> class="active" <?php }
				?>><a href="<?php echo htmlspecialchars($val['href']) ?>"<?php echo $this->skin->tooltipAndAccesskeyAttribs($val['id']) ?>><?php echo htmlspecialchars($val['text']) ?></a></li>
<?php			} ?>
			</ul>
<?php   } else {
			# allow raw HTML block to be defined by extensions
			print $cont;
		}
?>
		</div>
	</div>
<?php
	}
}
