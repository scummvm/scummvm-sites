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
const createLogger = require('logging').default;
const logger = createLogger('Stats');

const ProfileMappers = {
    "baseball": (profileFields) => {
        const profile = {
            wins: profileFields[0],
            losses: profileFields[1],
            disconnects: profileFields[2],
            winStreak: profileFields[3],
            lastTenGames: profileFields[4],
            margin: profileFields[5],
            careerTotalGames: profileFields[6],
            careerAtBats: profileFields[7],
            careerHits: profileFields[8],
            // NOTE: Batting average is fortunately calculated in-game,
            // setting this field in the database will not change anything.
            careerBattingAverage: profileFields[9],
            careerSingles: profileFields[10],
            careerDoubles: profileFields[11],
            careerTriples: profileFields[12],
            careerHomeRuns: profileFields[13],
            careerRuns: profileFields[14],
            careerSteals: profileFields[15],
            careerStrikeouts: profileFields[16],
            careerWalks: profileFields[17],
            gameHits: profileFields[18],
            gameSingles: profileFields[19],
            gameDoubles: profileFields[20],
            gameTriples: profileFields[21],
            gameHomeRuns: profileFields[22],
            gameRuns: profileFields[23],
            gameSteals: profileFields[24],
            gameStrikeouts: profileFields[25],
            gameWalks: profileFields[26],
            longestHomeRun: profileFields[27],
            poll: profileFields[28],
            // chatEnabled: profileFields[29]
        }
        return profile;
    }
}

const ResultsMappers = {
    // These take an array that the game sends to `/game_results`
    // and return an ongoing results object that can be stored in redis
    "baseball": (resultsFields, isHome, opponentId, last) => {
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
            last: last,
        };
        return ongoingResults;
    },
    "football": (resultsFields, isHome, opponentId, last) => {
        const ongoingResults = {
            winning: resultsFields[0],
            score: resultsFields[1],
            passingYards: resultsFields[2],
            passingAttempts: resultsFields[3],
            completePasses: resultsFields[4],
            rushingYards: resultsFields[5],
            rushingAttempts: resultsFields[6],
            // NOTE: field 7 is rushing completes, but is commented
            // off the original network code, so this is omitted.
            fumbles: resultsFields[8],
            fumblesLost: resultsFields[9],
            fieldGoalAttempts: resultsFields[10],
            fieldGoalsMade: resultsFields[11],
            puntAttempts: resultsFields[12],
            puntYards: resultsFields[13],
            puntBlocks: resultsFields[14],
            thirdDowns: resultsFields[15],
            thirdDownsConverted: resultsFields[16],
            fourthDowns: resultsFields[17],
            fourthDownsConverted: resultsFields[18],
            defenseInterceptions: resultsFields[19],
            defenseFumbles: resultsFields[20],
            defenseSacks: resultsFields[21],
            longestPass: resultsFields[22],
            puntReturn: resultsFields[23],
            opponentDefenseInterceptions: resultsFields[24],
            opponentPassingYards: resultsFields[25],
            opponentRushingYards: resultsFields[26],
            opponentScore: resultsFields[27],
            opponentThirdDowns: resultsFields[28],
            opponentThirdDownsConverted: resultsFields[29],
            opponentFourthDowns: resultsFields[30],
            opponentFourthDownsConverted: resultsFields[31],
            disconnect: resultsFields[32],
            quarter: resultsFields[33],
            isHome: isHome,
            opponentId: opponentId,
            last: last
        };
        return ongoingResults;
    }
};

const CalculateStats = {
    "baseball": async (userId, gameResults, opponentId, opponentGameResults) => {
        const user = await redis.getUserById(userId, "baseball");
        if (Object.keys(user).length == 0) {
            // TODO: User must've disconnected from the lobby, get
            // stats from the WebAPI and work from there.
            logger.warn(`TODO: User ${userId} not in redis.`);
            return
        }
        const stats = ProfileMappers["baseball"](user.stats);

        const opponent = await redis.getUserById(opponentId, "baseball");
        if (Object.keys(opponent).length == 0) {
            // TODO: User must've disconnected from the lobby, get
            // stats from the WebAPI and work from there.
            logger.warn(`TODO: User ${opponentId} not in redis.`);
            return
        }
        const opponentStats = ProfileMappers["baseball"](opponent.stats);

        function getLastTenWinLosses(value) {
            return [value & 1023, value >> 10];
        }

        function convertLastTenWinLosses([wins, losses]) {
            let value = losses << 10;
            value += wins;
            return value;
        }

        function calculateWinLoss(stats, gameResults) {
            let [lastTenWins, lastTenLosses] = getLastTenWinLosses(stats.lastTenGames);
            if (gameResults["winning"]) {
                // Record win.
                stats.wins += 1;
                stats.winStreak += 1;
                if (lastTenWins < 10) {
                    lastTenWins++;
                }
                if (lastTenLosses > 0) {
                    lastTenLosses--;
                }
            } else {
                // Record loss.
                stats.losses += 1;
                if (gameResults["disconnect"]) {
                    stats.disconnects += 1;
                }
                stats.winStreak = 0;
                if (lastTenWins > 0) {
                    lastTenWins--;
                }
                if (lastTenLosses < 10) {
                    lastTenLosses++;
                }
            }

            stats.lastTenGames = convertLastTenWinLosses([lastTenWins, lastTenLosses]);

            // TODO: Calculate stats.margin.
        }

        function calculateCareerRecords(stats, gameResults) {
            // Career records
            stats.careerTotalGames++;
            stats.careerAtBats += gameResults["atBats"];
            stats.careerHits += gameResults["hits"];
            // The game calculates the batting average, so skipping.
            stats.careerSingles += gameResults["singles"]
            stats.careerDoubles += gameResults["doubles"]
            stats.careerTriples += gameResults["triples"]
            stats.careerHomeRuns += gameResults["homeRuns"]
            stats.careerRuns += gameResults["runs"]
            stats.careerSteals += gameResults["steals"]
            stats.careerStrikeouts += gameResults["strikeouts"]
            stats.careerWalks += gameResults["walks"]

            // We don't know what the "game" stats are used for, so we're ignoring them for now.

            if (gameResults["longestHomeRun"] > stats.longestHomeRun) {
                stats.longestHomeRun = gameResults["longestHomeRun"]
            }
        }

        // Check for disconnects.  This value gets set when someone loses connection to their other player
        // (1), or forfeits a match (2), and it could happen either they were winning or not.
        // We do this check so the disconnector will be credited as a lost and their opponent
        // as a winner.
        if (gameResults["disconnect"]) {
            opponentGameResults["winning"] = 1;
            gameResults["winning"] = 0;
        } else if (opponentGameResults["disconnect"]) {
            gameResults["winning"] = 1;
            opponentGameResults["winning"] = 0;
        }

        // Calculate win/losses
        calculateWinLoss(stats, gameResults);
        calculateWinLoss(opponentStats, opponentGameResults);

        calculateCareerRecords(stats, gameResults);
        calculateCareerRecords(opponentStats, opponentGameResults);

        return [stats, opponentStats];
    },
    "football": async (userId, gameResults, opponentId, opponentGameResults) => {
        // TODO: Football stats
        return [{}, {}]
    }
}

module.exports = {
    ProfileMappers: ProfileMappers,
    ResultsMappers: ResultsMappers,
    CalculateStats: CalculateStats,
};
