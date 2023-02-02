# Games to accept:
GAMES = [
	"football", # Backyard Football (1999)
	"baseball2001", # Backyard Baseball 2001
	"football2002", # Backyard Football 2002 
	"moonbase", # Moonbase Commander (v1.0/v1.1/Demo)
]

# Full names of accepted games.  Make sure that they
# match with the GAMES list above
NAMES = {
	"football": "Backyard Football",
	"baseball2001": "Backyard Baseball 2001",
	"football2002": "Backyard Football 2002",
	"moonbase": "Moonbase Commander"
}

# Version variants to accept for a specific game.
# If none exist but game exist in the GAMES list,
# that means there's only one game version.
VERSIONS = {
	"moonbase": ["1.0", "1.1", "Demo"]
}