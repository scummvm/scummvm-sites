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
const logger = createLogger('AreaMessages');

const Areas = require('../global/Areas.js');
const logEvent = require('../global/EventLogger.js').logEvent;

server.handleMessage('get_population', async (client, args) => {
    const areaId = args.area;
    if (areaId === undefined) {
        logger.warn('Got get_population message without area id!  Ignoring.');
        return;
    }

    let population = 0;
    if (areaId in Areas.Groups) {
        for (const area of Areas.Groups[areaId]) {
            const users = await redis.getUsersInArea(area, client.game);
            for (const user of users) {
                if (client.versionNumber == user.version)
                    population += 1
            }
        }
    } else {
        const users = await redis.getUsersInArea(areaId, client.game);
        for (const user of users) {
            if (client.versionNumber == user.version)
                population += 1
        }
    }
    client.send('population_resp', {area: areaId, population: population});

});

server.handleMessage('enter_area', async (client, args) => {
    const areaId = args.area;
    logEvent('enter_area', client, args.version, {'area': areaId});
    if (areaId === undefined) {
        logger.warn('Got enter_area message without area id!  Ignoring.');
        return;
    }
    if (areaId == 33) {
        // HACK
        return;
    }
    client.areaId = areaId;
    await redis.addUserToArea(client.userId, areaId, client.game);
});

server.handleMessage('leave_area', async (client, args) => {
    logEvent('leave_area', client, args.version, {'area': client.areaId});
    if (!client.areaId) {
        // this.logger.error("Got leave_area without being in an area!");
        return;
    }
    const oldAreaId = client.areaId;
    client.areaId = 0;
    client.sliceStart = 0;
    client.sliceEnd = 0;
    await redis.removeUserFromArea(client.userId, oldAreaId, client.game);
});

server.handleMessage('get_players', async (client, args) => {
    const start = args.start;
    const end = args.end + 1;

    if (!client.areaId) {
        logger.warn("Got get_players without being in an area!");
        return;
    }

    client.sliceStart = start;
    client.sliceEnd = end;

    const users = await redis.getUsersInArea(client.areaId, client.game);

    const players = [];
    for (const user of users) {
        if ((user.id == client.userId) || (user.version != client.versionNumber)) {
            // Don't add ourselves or mismatched versions in.
            continue;
        }
        players.push([user.user, user.id, user.icon, user.stats[0], user.stats[1], user.stats[2], user.phone, user.opponent]);
    }
    client.send('players_list', {players: players.slice(client.sliceStart, client.sliceEnd)});

});

process.on('update_players_list', (args) => {
    const areaId = args.area;
    const game = args.game;
    const users = args.users;

    for (const client of server.connections) {
        if (client.areaId == areaId && client.game == game) {
            const players = [];
            for (const user of users) {
                if ((user.id == client.userId) || (user.version != client.versionNumber)) {
                    // Don't add ourselves or mismatched versions in.
                    continue;
                }
                players.push([user.user, user.id, user.icon, user.stats[0], user.stats[1], user.stats[2], user.phone, user.opponent]);
            }
            client.send('players_list', {players: players.slice(client.sliceStart, client.sliceEnd)});
        }
    }
});

server.handleMessage('game_started', async (client, args) => {
    const playerId = args.user;
    logEvent('game_started', client, args.version, {'area': client.areaId, 'opponent': playerId});

    await redis.setInGame(client.userId, 1);
    await redis.setInGame(playerId, 1);

    await redis.sendUsersInArea(client.areaId, client.game);
    await redis.sendGamesPlayingInArea(client.areaId, client.game);

    await redis.removeOngoingResults(client.userId, client.game);  // Just in case ongoing results didn't get removed after a previous game
    await redis.removeOngoingResults(playerId, client.game);
});

server.handleMessage('game_finished', async (client, args) => {
    logEvent('game_finished', client, args.version, {'area': client.areaId, 'opponent': client.opponentId});
    await redis.setInGame(client.userId, 0);
    await redis.sendGamesPlayingInArea(client.areaId, client.game);
});

process.on('update_games_playing', async (args) => {
    const areaId = args.area;
    const game = args.game;
    const gamesPlaying = args.games;

    for (const client of server.connections) {
        if (client.areaId == areaId && client.game == game) {
            client.send('games_playing', {games: gamesPlaying});
        }
    }
});