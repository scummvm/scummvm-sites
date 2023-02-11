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
            const users = await redis.getUserIdsInArea(area, client.game);
            population += users.length;
        }
    } else {
        population = (await redis.getUserIdsInArea(areaId, client.game)).length;
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
        if (user.id == client.userId) {
            // Don't add ourselves in.
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
                if (user.id == client.userId) {
                    // Don't add ourselves in.
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

    await redis.removeOngoingResults(client.opponentId, client.game);
    await redis.removeOngoingResults(client.userId, client.game);
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
