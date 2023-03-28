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

const ResultsMappers = {
    // These take an array that the game sends to `/game_results`
    // and return an ongoing results object that can be stored in redis
    "baseball": (resultsFields, isHome, opponentId) => {
        const ongoingResults = {
            winning: resultsFields[0],
            runs: resultsFields[1],
            atBats: resultsFields[2],
            hits: resultsFields[3],
            homeRuns: resultsFields[4],
            longestHomeRun: resultsFields[5],
            singles: resultsFields[6],
            doubles: resultsFields[7],
            triples: resultsFields[8],
            steals: resultsFields[9],
            strikeouts: resultsFields[10],
            walks: resultsFields[11],
            disconnect: resultsFields[12],
            completedInnings: resultsFields[13],
            isHome: isHome,
            opponentId: opponentId,
        };
        return ongoingResults;
    },
    // TODO: Football
    "football": (resultsFields, isHome, opponentId) => {
        return {"not_yet_supported": 1}
    }
};

module.exports = {
    ResultsMappers: ResultsMappers,
};
