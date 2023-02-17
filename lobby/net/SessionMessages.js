"use strict";
const createLogger = require('logging').default;
const logger = createLogger('SessionMessages');

const logEvent = require('../global/EventLogger.js').logEvent;

server.handleMessage('send_session', async (client, args) => {
    const userId = args.user;
    const sessionId = args.session;
    logEvent('send_session', client, args.version, {'session': sessionId, 'opponent': userId});

    if (userId === undefined) {
        logger.error("Missing user argument on send_session!");
        return;
    } else if (client.areaId == 0) {
        logger.error(`Got send_session but I'm (${client.userId}) not in an area!`);
        return;
    }

    // Check if the opponent is in our area.
    const users = await redis.getUserIdsInArea(client.areaId, client.game);
    if (!users.includes(userId)) {
        logger.error(`Got send_session but our player (${userId}) isn't in area (${client.areaId})!`);
        return;
    }

    process.send({cmd: 'game_session', user: userId,
                                       opponent: client.userId,
                                       session: sessionId});
});

process.on('game_session', async (args) => {
    const userId = args.user;
    const opponentId = args.opponent;
    const sessionId = args.session;

    for (const client of server.connections) {
        if (client.userId == userId) {
            if (client.areaId == 0) {
                logger.error(`Got game_session but I'm (${client.userId}) not in an area!`);
                return;
            }
            // Check if the opponent is in our area.
            const users = await redis.getUserIdsInArea(client.areaId, client.game);
            if (!users.includes(opponentId)) {
                logger.error(`Got game_session but our player (${opponentId}) isn't in area (${client.areaId})!`);
                return;
            }

            client.send("game_session", {session: sessionId});
            return;
        }
    }
});
