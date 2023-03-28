/* ScummVM - Graphic Adventure Engine
 *
 * ScummVM is the legal property of its developers, whose names
 * are too numerous to list here. Please refer to the COPYRIGHT
 * file distributed with this source distribution.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

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
