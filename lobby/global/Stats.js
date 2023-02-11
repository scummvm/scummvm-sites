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