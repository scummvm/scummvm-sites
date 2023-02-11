"use strict";

const Areas = {
    // Easy Street
    8: "Wilderness",
    9: "Mountain Aire",
    // Mediumville
    16: "Dogwood",
    17: "Brookline",
    18: "Talula Lake",
    19: "Prince Rupert",
    // Toughy Town
    24: "Vespucci Park",
    25: "Capitol Hill",
    26: "Lewis Ave.",

    33: "Baseball 2001 Lobby"
};

const Groups = {
    // Easy Street
    '-248': [8, 9],
    // Mediumville
    '-240': [16, 17, 18, 19],
    // Toughy Town
    '-232': [24, 25, 26]
};

module.exports = {
    Areas: Areas,
    Groups: Groups
};
