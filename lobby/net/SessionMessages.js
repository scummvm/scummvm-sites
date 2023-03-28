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
