"use strict";
const createLogger = require('logging').default;
const logger = createLogger('ChallengeMessages');

const logEvent = require('../global/EventLogger.js').logEvent;

// Hack for baseball
const busyTimeouts = {};

server.handleMessage('set_phone_status', async (client, args) => {
    const status = args.status;
    if (status === undefined) {
        return;
    }
    if (!client.areaId) {
        logger.warn('Attempted to set phone status without being in an area.');
        return;
    }

    await redis.setPhoneStatus(client.userId, client.areaId, client.game, status);
});

server.handleMessage('challenge_player', async (client, args) => {
    const challengeUserId = args.user;
    const stadium = args.stadium;
    logEvent('challenge_player', client, args.version, {'area': client.areaId, 'opponent': challengeUserId, 'stadium': stadium});

    if (challengeUserId === undefined) {
        logger.error("Missing user argument on challenge_player!");
        return;
    } else if (stadium === undefined) {
        logger.error("Missing stadium argument for challenge_player!");
        return;
    } else if (client.areaId == 0) {
        logger.error(`Got challenge_player but I'm (${client.userId}) not in an area!`);
        return;
    }

    // Check if the opponent is in our area.
    const users = await redis.getUserIdsInArea(client.areaId, client.game);
    if (!users.includes(challengeUserId)) {
        logger.error(`Got challenge_player but our player (${challengeUserId}) isn't in area (${client.areaId})!`);
        return;
    }

    if (client.userId in busyTimeouts) {
        clearTimeout(busyTimeouts[client.userId]);
    }

    process.send({cmd: "receive_challenge", user: challengeUserId,
                                            opponent: client.userId,
                                            stadium: stadium});
});

process.on('receive_challenge', async (args) => {
    const userId = args.user;
    const opponentId = args.opponent;
    const stadium = args.stadium;

    for (const client of server.connections) {
        if (client.userId == userId) {
            if (client.areaId == 0) {
                logger.error(`Got receive_challenge from server but I'm (${client.userId}) not in an area!`);
                return;
            } else if (stadium === undefined) {
                logger.error("Missing stadium argument for receive_challenge!");
                return;
            }
            // Check if the opponent is in our area.
            const users = await redis.getUserIdsInArea(client.areaId, client.game);
            if (!users.includes(opponentId)) {
                logger.error(`Got receive_challenge but our player (${opponentId}) isn't in area (${client.areaId})!`);
                return;
            }

            const userData = await redis.getUserById(opponentId);
            if (Object.keys(userData).length == 0) {
                logger.error(`Got receive_challenge but our player (${opponentId}) doesn't exist!`);
                return;
            }
            client.send("receive_challenge", {user: opponentId, stadium: stadium, name: userData.user.toUpperCase()});
            return;
        }
    }
});

server.handleMessage('challenge_timeout', async (client, args) => {
  const challengeUserId = args.user;
  logEvent('challenge_timeout', client, args.version, {'area': client.areaId, 'opponent': challengeUserId});
  if (challengeUserId === undefined) {
      logger.error("Missing user argument on challenge_timeout!");
      return;
  } else if (client.areaId == 0) {
      logger.error(`Got challenge_timeout but I'm (${client.userId}) not in an area!`);
      return;
  }

  // Check if the opponent is in our area.
  const users = await redis.getUserIdsInArea(client.areaId, client.game);
  if (!users.includes(challengeUserId)) {
      logger.error(`Got challenge_timeout but our player (${challengeUserId}) isn't in area (${client.areaId})!`);
      return;
  }

  process.send({cmd: "challenge_timeout", user: challengeUserId,
                                          opponent: client.userId});
});

process.on('challenge_timeout', async (args) => {
    const userId = args.user;
    const opponentId = args.opponent;

    for (const client of server.connections) {
        if (client.userId == userId) {
            if (client.areaId == 0) {
                logger.error(`Got challenge_timeout from server but I'm (${client.userId}) not in an area!`);
                return;
            }

            // Check if the opponent is in our area.
            const users = await redis.getUserIdsInArea(client.areaId, client.game);
            if (!users.includes(opponentId)) {
                logger.error(`Got challenge_timeout but our player (${opponentId}) isn't in area (${client.areaId})!`);
                return;
            }
            client.send("decline_challenge", {not_responding: 1});
            return;
        }
    }
});

server.handleMessage('receiver_busy', async (client,args) => {
    const userId = args.user;

    if (userId === undefined) {
        logger.error("Missing user argument on receiver_busy!");
        return;
    } else if (client.areaId == 0) {
        logger.error(`Got receiver_busy but I'm (${client.userId}) not in an area!`);
        return;
    }

    const users = await redis.getUserIdsInArea(client.areaId, client.game);
    if (!users.includes(userId)) {
        logger.error(`Got receiver_busy but our player (${userId}) isn't in area (${client.areaId})!`);
        return;
    }

    process.send({cmd: 'receiver_busy', user: userId,
                                        opponent: client.userId});
});

process.on('receiver_busy', async (args) => {
    const userId = args.user;
    const opponentId = args.opponent;

    for (const client of server.connections) {
        if (client.userId == userId) {
            if (client.areaId == 0) {
                logger.error(`Got receiver_busy but I'm (${client.userId}) not in an area!`);
                return;
            }
            // Check if the opponent is in our area.
            const users = await redis.getUserIdsInArea(client.areaId, client.game);
            if (!users.includes(opponentId)) {
                logger.error(`Got receiver_busy but our player (${opponentId}) isn't in area (${client.areaId})!`);
                return;
            }

            client.send("receiver_busy");

            // HACK: In baseball, the game does not automatically hang up
            // the phone and return to the users list.  We have to send a
            // decline_challenge message to get back there.
            // TODO: Possibly make this a client-sided hack?
            if (client.game == "baseball") {
                busyTimeouts[client.userId] = setTimeout((client) => {
                    client.send("decline_challenge", {not_responding: 1});
                }, 7000, client);
            }
            return;
        }
    }
});

server.handleMessage('considering_challenge', async (client, args) => {
    const userId = args.user;

    if (userId === undefined) {
        logger.error("Missing user argument on considering_challenge!");
        return;
    } else if (client.areaId == 0) {
        logger.error(`Got considering_challenge but I'm (${client.userId}) not in an area!`);
        return;
    }

    // Check if the opponent is in our area.
    const users = await redis.getUserIdsInArea(client.areaId, client.game);
    if (!users.includes(userId)) {
        logger.error(`Got considering_challenge but our player (${userId}) isn't in area (${client.areaId})!`);
        return;
    }

    client.opponentId = userId;
    process.send({cmd: 'considering_challenge', user: userId,
                                                opponent: client.userId});
});

process.on('considering_challenge', async (args) => {
    const userId = args.user;
    const opponentId = args.opponent;

    for (const client of server.connections) {
        if (client.userId == userId) {
            if (client.areaId == 0) {
                logger.error(`Got considering_challenge but I'm (${client.userId}) not in an area!`);
                return;
            }
            // Check if the opponent is in our area.
            const users = await redis.getUserIdsInArea(client.areaId, client.game);
            if (!users.includes(opponentId)) {
                logger.error(`Got considering_challenge but our player (${opponentId}) isn't in area (${client.areaId})!`);
                return;
            }

            client.opponentId = opponentId;
            client.send("considering_challenge");
            return;
        }
    }
});

server.handleMessage('counter_challenge', async (client, args) => {
    const stadium = args.stadium;
    logEvent('counter_challenge', client, args.version, {'area': client.areaId, 'opponent': client.opponentId, 'stadium': stadium});

    if (stadium === undefined) {
        logger.error("Got counter_challenge but stadium is not defined!");
        return;
    }
    else if (client.areaId == 0) {
        logger.error(`Got counter_challenge but I'm (${client.userId}) not in an area!`);
        return;
    }

    // Check if the opponent is in our area.
    const users = await redis.getUserIdsInArea(client.areaId, client.game);
    if (!users.includes(client.opponentId)) {
        logger.error(`Got counter_challenge but our player (${client.opponentId}) isn't in area (${client.areaId})!`);
        return;
    }

    process.send({cmd: 'counter_challenge', user: client.opponentId,
                                            stadium: stadium});
});

process.on('counter_challenge', async (args) => {
    const userId = args.user;
    const stadium = args.stadium;

    for (const client of server.connections) {
        if (client.userId == userId) {
            if (client.areaId == 0) {
                logger.error(`Got considering_challenge but I'm (${client.userId}) not in an area!`);
                return;
            }
            // Check if the opponent is in our area.
            const users = await redis.getUserIdsInArea(client.areaId, client.game);
            if (!users.includes(client.opponentId)) {
                logger.error(`Got considering_challenge but our player (${client.opponentId}) isn't in area (${client.areaId})!`);
                return;
            }
            client.send('counter_challenge', {stadium: stadium});
            return;
        }
    }
});

server.handleMessage('decline_challenge', async (client, args) => {
    const challengeUserId = args.user;
    logEvent('decline_challenge', client, args.version, {'area': client.areaId, 'opponent': challengeUserId});

    if (challengeUserId === undefined) {
        logger.error("Missing user argument on decline_challenge!");
        return;
    } else if (client.areaId == 0) {
        logger.error(`Got decline_challenge but I'm (${client.userId}) not in an area!`);
        return;
    }

    // Check if the opponent is in our area.
    const users = await redis.getUserIdsInArea(client.areaId, client.game);
    if (!users.includes(challengeUserId)) {
        logger.error(`Got decline_challenge but our player (${challengeUserId}) isn't in area (${client.areaId})!`);
        return;
    }

    client.opponentId = 0;
    process.send({cmd: 'decline_challenge', user: challengeUserId,
                                            opponent: client.userId,
                                            not_responding: 0});
});

process.on('decline_challenge', async (args) => {
    const userId = args.user;
    const opponentId = args.opponent;
    const notResponding = args.not_responding;

    for (const client of server.connections) {
        if (client.userId == userId) {
            if (client.areaId == 0) {
                logger.error(`Got decline_challenge but I'm (${client.userId}) not in an area!`);
                return;
            }
            // Check if the opponent is in our area.
            const users = await redis.getUserIdsInArea(client.areaId, client.game);
            if (!users.includes(opponentId)) {
                logger.error(`Got decline_challenge but our player (${opponentId}) isn't in area (${client.areaId})!`);
                return;
            }

            client.opponentId = 0;
            client.send("decline_challenge", {not_responding: notResponding});
            return;
        }
    }
});

server.handleMessage('accept_challenge', async (client, args) => {
    const challengeUserId = args.user;
    logEvent('accept_challenge', client, args.version, {'area': client.areaId, 'opponent': challengeUserId});

    if (challengeUserId === undefined) {
        logger.error("Missing user argument on accept_challenge!");
        return;
    } else if (client.areaId == 0) {
        logger.error(`Got accept_challenge but I'm (${client.userId}) not in an area!`);
        return;
    }

    // Check if the opponent is in our area.
    const users = await redis.getUserIdsInArea(client.areaId, client.game);
    if (!users.includes(challengeUserId)) {
        logger.error(`Got accept_challenge but our player (${challengeUserId}) isn't in area (${client.areaId})!`);
        return;
    }

    client.opponentId = challengeUserId;
    process.send({cmd: 'accept_challenge', user: challengeUserId,
                                           opponent: client.userId});
});

process.on('accept_challenge', async (args) => {
    const userId = args.user;
    const opponentId = args.opponent;

    for (const client of server.connections) {
        if (client.userId == userId) {
            if (client.areaId == 0) {
                logger.error(`Got accept_challenge but I'm (${client.userId}) not in an area!`);
                return;
            }
            // Check if the opponent is in our area.
            const users = await redis.getUserIdsInArea(client.areaId, client.game);
            if (!users.includes(opponentId)) {
                logger.error(`Got accept_challenge but our player (${opponentId}) isn't in area (${client.areaId})!`);
                return;
            }

            client.opponentId = opponentId;
            client.send("accept_challenge");
            return;
        }
    }
});
