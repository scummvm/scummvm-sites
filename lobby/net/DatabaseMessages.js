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
const logger = createLogger('DatabaseMessages');

const Areas = require('../global/Areas.js');
const Stats = require('../global/Stats.js');
const logEvent = require('../global/EventLogger.js').logEvent;

server.handleMessage("login", async (client, args) => {
    const username = args.user;
    const password = args.pass;
    const game = args.game;
    const version = args.version;
    const competitive_mods = args.competitive_mods;

    if (username === undefined) {
        client.kick("Missing username parameter!");
        return;
    } else if (password === undefined) {
        client.kick("Missing password parameter!");
        return;
    } else if (game === undefined) {
        client.kick("Missing game parameter!");
        return;
    } else if (version == undefined) {
        client.kick("Missing version paremeter!");
        return;
    }

    const games = ["football", "baseball"];
    if (!games.includes(game)) {
        client.kick("Game not supported.");
        return;
    }
    client.game = game;
    client.version = version;
    client.competitiveMods = competitive_mods || false;

    const user = await database.getUser(username, password, game);
    logEvent('login', client, args.version, {'user': user.id, 'username': user.user, 'game': game, 'competitive_mods': competitive_mods});
    if (user.error) {
        client.send("login_resp", {error_code: user.error,
                                   id: 0,
                                   sessionServer: "",
                                   response: user.message});
        return;
    }

    // Kick the other clients out if they're logged in
    // as the same user.
    process.send({cmd: 'kick',
                  userId: user.id,
                  type: 901,
                  reason: "You have been disconnected because someone else just logged in using your account on another computer."});

    // We finish setting up the login details at the end of the event loop
    // to prevent ourselves from getting kicked out after logging in.
    setTimeout(() => {
        client.userId = user.id;
        client.send("login_resp", {error_code: 0,
                                   id: user.id,
                                   sessionServer: server.sessionServer,
                                   response: "All ok"});

    }, 50);
});

server.handleMessage('get_profile', async (client, args) => {
    let userId = args.user_id;
    if (userId === undefined) {
        // Must be self.
        userId = client.userId;
    }
    const user = await redis.getUserById(userId, client.game);
    if (Object.keys(user).length == 0)
        return;

    const profile = [user.icon].concat(user.stats);
    client.send("profile_info", {profile: profile});
});

server.handleMessage('download_file', async (client, args) => {
    const filename = args.filename;
    logEvent('download_file', client, args.version, {'filename': filename});

    let data = "";
    if (filename == "news.ini") {
        const news = await database.getNews();
        if (!news.error)
            data = news.news;
    }

    client.send("file_data", {filename: filename, data: data});
});

server.handleMessage('set_icon', async (client, args) => {
    const icon = args.icon;
    logEvent('set_icon', client, args.version, {'icon': icon});

    if (client.userId == 0) {
        client.kick("Attempting to set icon without logging in first.");
        return;
    } else if (icon === undefined) {
        logger.warn("Got set_icon with missing icon!  Ignoring.");
        return;
    }

    await database.setIcon(client.userId, icon);
});

server.handleMessage('locate_player', async (client, args) => {
    const username = args.user;
    if (client.userId == 0) {
        client.kick("Attempting to locate player without logging in first.");
        return;
    } else if (username == undefined) {
        logger.warn("Got locate_user without username set.  Ignoring.");
        return;
    }

    const response = {code: 0,
                      areaId: 0,
                      area: ""};

    const user = await redis.getUserByName(username);
    if (!user || !user.game || user.game != client.game) {
        // Player not logged in or in the different game
        client.send("locate_resp", response);
        return
    }

    if (!user.area) {
        // Logged in but not in an area.
        response.code = 4;
    } else if (user.inGame) {
        response.code = 2;
    } else {
        response.code = 1;
        response.areaId = user.area;
        response.area = Areas.Areas[user.area] || `Unknown area (${user.area})`;
    }

    client.send("locate_resp", response);
});

server.handleMessage("game_results", async (client, args) => {
    const resultsUserId = args.user;
    const reportingUserId = client.userId;
    let isHome;
    let opponentId;
    // The home team always reports the game results, so we can use that
    // to tell whether the results are for the home or away team.
    // TODO: Verify that this is true for football (it is for baseball)
    if (reportingUserId == resultsUserId) {
        isHome = 1;
        opponentId = client.opponentId;
    } else {
        isHome = 0;
        opponentId = client.userId;
    }
    const resultsFields = args.fields;
    const ongoingResults = Stats.ResultsMappers[client.game](
        resultsFields, isHome, opponentId
    );
    logEvent('game_results', client, args.version, {'results': ongoingResults, 'rawResults': resultsFields});

    await redis.setOngoingResults(resultsUserId, client.game, ongoingResults);
});

server.handleMessage('get_teams', async (client, args) => {
    const userId = client.userId;
    const opponentId = args.opponent_id;

    const game = client.game;

    const userTeamResponse = await database.getTeam(userId, game);
    const opponentTeamResponse = await database.getTeam(opponentId, game);

    logEvent('get_teams', client, args.version, {'userTeam': userTeamResponse, 'opponentTeam': opponentTeamResponse});

    let responseErrorMessages = [];
    if (userTeamResponse.error) {
        responseErrorMessages.push("User: " + userTeamResponse.message);
    }
    if (opponentTeamResponse.error) {
        responseErrorMessages.push("Opponent: " + opponentTeamResponse.message);
    }

    if (responseErrorMessages.length > 0) {
        const fullErrorMessage = responseErrorMessages.join(" ");
        client.send("teams", {error: 1, message: fullErrorMessage, user: [], opponent: []});
        return;
    }

    let duplicatePlayers = userTeamResponse.team.filter(
        player => opponentTeamResponse.team.indexOf(player) != -1
    );
    if (duplicatePlayers.length > 0) {
        client.send("teams", {
            error: 1,
            message: `Both teams have the same player(s): ${duplicatePlayers.join(", ")}`,
            user: [],
            opponent: []
        });
        return;
    }

    const teams = {error: 0, message: "", user: userTeamResponse.team, opponent: opponentTeamResponse.team};
    client.send("teams", teams);
});
