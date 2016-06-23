# This file should contain all the record creation needed to seed the database with its default values.
# The data can then be loaded with the rake db:seed (or created alongside the db with db:setup).

unless Platform.any?
  [ "Unknown", "DOS", "Amiga", "AtariST", "Macintosh", "FMTowns", "Windows", "NES",
    "C64", "CoCo3", "Linux", "Acorn", "SegaCD", "3DO", "PCEngine", "Apple2", "Apple2GS",
    "PC98", "Wii", "PSX", "CDi", "IOS", "OS2", "BeOS"
  ].each { |p| Platform.create name: p }
end

unless Language.any?
  [ "EN_ANY",  # Generic English (when only one game version exist)
    "EN_USA", "EN_GRB", "CZ_CZE", "DE_DEU", "ES_ESP", "FR_FRA", "GR_GRE", "HE_ISR",
    "HR_HRV", "HU_HUN", "IT_ITA", "JA_JPN", "KO_KOR", "LV_LAT", "NB_NOR", "NL_NLD",
    "PL_POL", "PT_BRA", "RU_RUS", "SE_SWE", "ZH_CNA", "ZH_TWN", "UNK_LANG"
  ].each { |p| Language.create code: p }
end

Engine.create(name: "Access").games.create([
  { name: "Amazon: Guardians of Eden" }
]) rescue nil
Engine.create(name: "AGI").games.create([
{ name: "Dragon's Keep", first_release: 1982, developer: "Sierra" },
{ name: "The Gelfling Adventure", first_release: 1983, developer: "Sierra" },
{ name: "Troll's Tale", first_release: 1983, developer: "Sierra" },
{ name: "Mickey's Space Adventure", first_release: 1984, developer: "Sierra" },
{ name: "Winnie the Pooh in the Hundred Acre Wood", first_release: 1984, developer: "Sierra" },
{ name: "King's Quest", first_release: 1984, developer: "Sierra" },
{ name: "King's Quest II", first_release: 1985, developer: "Sierra" },
{ name: "The Black Cauldron", first_release: 1986, developer: "Sierra" },
{ name: "Donald Duck's Playground", first_release: 1986, developer: "Sierra" },
{ name: "King's Quest III", first_release: 1986, developer: "Sierra" },
{ name: "Space Quest", first_release: 1986, developer: "Sierra" },
{ name: "Christmas Card 1986", first_release: 1986, developer: "Sierra" },
{ name: "AGI Demo Pack", first_release: 1987, developer: "Sierra" },
{ name: "Leisure Suit Larry", first_release: 1987, developer: "Sierra" },
{ name: "Mixed-Up Mother Goose", first_release: 1987, developer: "Sierra" },
{ name: "Police Quest", first_release: 1987, developer: "Sierra" },
{ name: "Space Quest II", first_release: 1987, developer: "Sierra" },
{ name: "Gold Rush", first_release: 1988, developer: "Sierra" },
{ name: "King's Quest IV", first_release: 1988, developer: "Sierra" },
{ name: "Manhunter", first_release: 1988, developer: "Sierra" },
{ name: "Manhunter 2", first_release: 1989, developer: "Sierra" }
]) rescue nil
Engine.create(name: "AGOS").games.create([
{ name: "Elvira: Mistress of the Dark" },
{ name: "Elvira 2: The Jaws of Cerberus" },
{ name: "The Feeble Files" },
{ name: "Personal Nightmare" },
{ name: "Simon the Sorcerer" },
{ name: "Simon the Sorcerer II: The Lion, the Wizard and the Wardrobe" },
{ name: "Simon the Sorcerer Puzzle Pack" },
{ name: "Waxworks" }
]) rescue nil
Engine.create(name: "BBVS").games.create([
{ name: "Beavis and Butt-Head in Virtual Stupidity" }
]) rescue nil
Engine.create(name: "CGE").games.create([
{ name: "Soltys" }
]) rescue nil
Engine.create(name: "CGE2").games.create([
{ name: "Sfinx" }
]) rescue nil
Engine.create(name: "Cine").games.create([
{ name: "Future Wars" }
]) rescue nil
Engine.create(name: "Composer").games.create([
{ name: "Darby the Dragon" },
{ name: "Gregory and the Hot Air Balloon" },
{ name: "Magic Tales: Liam Finds a Story" },
{ name: "Magic Tales: Sleeping Cub's Test of Courage" },
{ name: "Magic Tales: The Princess and the Crab" }
]) rescue nil
Engine.create(name: "CruisE").games.create([
{ name: "Cruise for a Corpse" }
]) rescue nil
Engine.create(name: "Draci").games.create([
{ name: "Dragon History" }
]) rescue nil
Engine.create(name: "Drascula").games.create([
{ name: "Drascula: The Vampire Strikes Back" }
]) rescue nil
Engine.create(name: "Dreamweb").games.create([
{ name: "Dreamweb" }
]) rescue nil
# Engine.create(name: "Gob").games.create([

# ])
# Engine.create(name: "Groovie").games.create([

# ])
# Engine.create(name: "Hopkins").games.create([

# ])
# Engine.create(name: "Hugo").games.create([

# ])
# Engine.create(name: "Kyra").games.create([

# ])
# Engine.create(name: "Lab").games.create([

# ])
# Engine.create(name: "Lure").games.create([

# ])
# Engine.create(name: "MADE").games.create([

# ])
# Engine.create(name: "MADS").games.create([

# ])
# Engine.create(name: "Mohawk").games.create([

# ])
# Engine.create(name: "Mortevielle").games.create([

# ])
# Engine.create(name: "Neverhood").games.create([

# ])
# Engine.create(name: "Parallaction").games.create([

# ])
# Engine.create(name: "Pegasus").games.create([

# ])
# Engine.create(name: "Queen").games.create([

# ])
# Engine.create(name: "SAGA").games.create([

# ])
# Engine.create(name: "SCI").games.create([

# ])
# Engine.create(name: "SCUMM").games.create([

# ])
# Engine.create(name: "Sherlock").games.create([

# ])
# Engine.create(name: "Sky").games.create([

# ])
# Engine.create(name: "Sword1").games.create([

# ])
# Engine.create(name: "Sword2").games.create([

# ])
# Engine.create(name: "Sword25").games.create([

# ])
# Engine.create(name: "Teenagent").games.create([

# ])
# Engine.create(name: "Tinsel").games.create([

# ])
# Engine.create(name: "Toltecs").games.create([

# ])
# Engine.create(name: "Tony").games.create([

# ])
# Engine.create(name: "Toon").games.create([

# ])
# Engine.create(name: "Touche").games.create([

# ])
# Engine.create(name: "TsAGE").games.create([

# ])
# Engine.create(name: "Tucker").games.create([

# ])
# Engine.create(name: "Voyeur").games.create([

# ])
# Engine.create(name: "Wintermute").games.create([

# ])
# Engine.create(name: "ZVision").games.create([

# ])