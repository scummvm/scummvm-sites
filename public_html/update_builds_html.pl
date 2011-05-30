#!/usr/bin/perl
# This perl script is used to regenerate builds.html.
# It is rather crude right now, feel free to improve it :).

use strict;

my $html_header = "";
my $html_footer = "";

open FILE, "builds.html.head" or die "Couldn't open file: $!";
$html_header = join("", <FILE>);
close FILE;

open FILE, "builds.html.foot" or die "Couldn't open file: $!";
$html_footer = join("", <FILE>);
close FILE;


open FILE, ">builds.html" or die "Couldn't open file: $!";
print FILE $html_header;


sub add_platform {
	my $icon = shift;
	my $file_abbrev = shift;
	my $desc = shift;
	# TODO: Display more info, e.g. file sizes and build date (that would require using
	# PHP or SSI or something like that)

	print FILE '<tr align="center">';
	print FILE '<td style="text-align: left; " class="row1" valign="middle">';
	print FILE '<img style="width: 24px; height: 24px;" alt=""';
	print FILE 'src="http://www.scummvm.org/images/catpl-' . $icon . '.png">' . $desc;
	print FILE '</td>';

	print FILE '<td style="text-align: center; width: 20em;" class="row1">';
	print FILE '<a href="/snapshots/master/' . $file_abbrev . '-master-latest.tar.bz2">Download latest development build</a>';
	print FILE '</td>';

	print FILE '<td style="text-align: center; width: 20em;" class="row1" nowrap="nowrap">';
	print FILE '<a href="/snapshots/stable/' . $file_abbrev . '-stable-latest.tar.bz2">Download latest stable build</a>';
	print FILE '</td>';
	print FILE '</tr>';
}

add_platform("android", "android", "Android");
add_platform("dc", "dc", "Dreamcast plain files");
add_platform("debian", "lenny", "Debian 'Lenny' 32bit");
add_platform("debian", "lenny-x86_64", "Debian 'Lenny' x64 64bit");
add_platform("dingux", "dingux", "Dingux");
add_platform("n64", "n64", "Nintendo 64");
add_platform("ds", "ds", "Nintendo DS");
add_platform("gc", "gamecube", "Nintendo Gamecube");
add_platform("wii", "wii", "Nintendo Wii");
add_platform("caanoo", "caanoo", "GamePark Caanoo");
add_platform("gp2x", "gp2x", "GamePark GP2X");
add_platform("gp2xwiz", "gp2xwiz", "GamePark GP2XWiz");
add_platform("iphone", "iphone", "iPhone");
add_platform("macos-universal", "osx_intel", "Mac OS X (Intel)");
add_platform("macos-universal", "osx_ppc", "Mac OS X (PowerPC)");
add_platform("linuxmoto", "motoezx", "Motorola (MotoEZX)");
add_platform("linuxmoto", "motomagx", "Motorola (MotoMAGX)");
add_platform("ps2", "ps2", "Playstation 2");
add_platform("psp", "psp", "Playstation Portable");
add_platform("webos", "webos", "HP webOS");
add_platform("windows", "mingw-w32", "Windows (32bit)");
add_platform("win64", "mingw-w64", "Windows (64bit)");
add_platform("wince", "wince", "Windows CE (ARM)");


print FILE $html_footer;
close FILE;