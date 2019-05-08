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
	my $build_tools = shift;
	my $archive_format = shift;
	# TODO: Display more info, e.g. file sizes and build date (that would require using
	# PHP or SSI or something like that)

	print FILE '<tr align="center">';
	print FILE '<td style="text-align: left; " class="row1">';
	print FILE '<img class="platform-icon" alt=""';
	print FILE 'src="https://www.scummvm.org/images/icons/platforms/' . $icon . '.png">' . $desc;
	print FILE '</td>';

	# master daily builds
	if (1) {
		print FILE '<td style="text-align: center; width: 20em;" class="row1">';
		print FILE '<a href="/snapshots/master/' . $file_abbrev . '-master-latest.' . $archive_format . '">Download latest development build</a>';
		print FILE '</td>';
	}

	# stable daily builds
	if (1) {
		print FILE '<td style="text-align: center; width: 20em;" class="row1" nowrap="nowrap">';
		print FILE '<a href="/snapshots/stable/' . $file_abbrev . '-stable-latest.' . $archive_format . '">Download latest stable build</a>';
		print FILE '</td>';
	}

	# tools master daily builds
	if (1) {
		print FILE '<td style="text-align: center; width: 20em;" class="row1">';
		if ($build_tools) {
			print FILE '<a href="/snapshots/tools-master/' . $file_abbrev . '-tools-master-latest.' . $archive_format . '">Download latest tools build</a>';
		} else {
			print FILE 'N/A';
		}
		print FILE '</td>';
	}

	print FILE '</tr>';
}

add_platform("amiga", "amigaos4", "Amiga OS4", "1", "zip");
add_platform("android", "android_arm", "Android (ARM)", "0", "zip");
add_platform("android", "android_arm64", "Android (ARM64)", "0", "zip");
add_platform("android", "android_x86", "Android (x86)", "0", "zip");
add_platform("dc", "dc", "Dreamcast plain files", "0", "tar.xz");
add_platform("dc", "dc-serial", "Dreamcast plain files with Serial Debug", "0", "tar.xz");
add_platform("debian", "debian-x86", "Debian 32bit", "1", "tar.xz");
add_platform("debian", "debian-x86_64", "Debian 64bit", "1", "tar.xz");
add_platform("dingux", "dingux", "Dingux", "0", "tar.xz");
add_platform("n64", "n64", "Nintendo 64", "0", "tar.xz");
add_platform("ds", "ds", "Nintendo DS", "0", "tar.xz");
add_platform("gc", "gamecube", "Nintendo Gamecube", "0", "tar.xz");
add_platform("wii", "wii", "Nintendo Wii", "0", "tar.xz");
add_platform("caanoo", "caanoo", "GamePark Caanoo", "0", "tar.bz2");
add_platform("gcw0", "gcw0", "GCW-Zero", "0", "tar.bz2");
add_platform("gp2x", "gp2x", "GamePark GP2X", "0", "tar.bz2");
add_platform("gp2xwiz", "gp2xwiz", "GamePark GP2XWiz", "0", "tar.bz2");
add_platform("iphone", "ios", "iOS (All Devices, iOS 3.1+)", "0", "tar.bz2");
add_platform("iphone", "ios7", "iOS (Modern Devices, iOS 7.1+)", "0", "tar.bz2");
#add_platform("iphone", "iphone-clang", "iPhone", "0", "tar.bz2");
add_platform("macos", "osx_intel", "Mac OS X (Intel)", "1", "tar.xz");
#add_platform("macosppc", "osx_ppc", "Mac OS X (PowerPC)", "1", "tar.xz");
#add_platform("linuxmoto", "motoezx", "Motorola (MotoEZX)", "0", "tar.xz");
#add_platform("linuxmoto", "motomagx", "Motorola (MotoMAGX)", "0", "tar.xz");
add_platform("openpandora", "openpandora", "OpenPandora", "0", "tar.bz2");
add_platform("android", "ouya", "OUYA", "0", "zip");
add_platform("ps2", "ps2", "Playstation 2", "0", "tar.xz");
add_platform("ps3", "ps3", "Playstation 3", "0", "tar.xz");
add_platform("psp", "psp", "Playstation Portable", "0", "tar.xz");
add_platform("psp2", "psp2", "Playstation Vita", "0", "zip");
add_platform("webos", "webos", "HP webOS", "0", "tar.xz");
add_platform("windows", "mingw-w32", "Windows (32bit)", "1", "zip");
add_platform("windows", "mingw-w64", "Windows (64bit)", "1", "zip");
#add_platform("wince", "wince", "Windows CE (ARM)", "0", "zip");
#add_platform("wince", "wince-split1", "Windows CE (ARM) - Split Build #1", "0", "zip");
#add_platform("wince", "wince-split2", "Windows CE (ARM) - Split Build #2", "0", "zip");
#add_platform("wince", "wince-split3", "Windows CE (ARM) - Split Build #3", "0", "zip");

print FILE $html_footer;
close FILE;
