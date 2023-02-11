"use strict";

const createLogger = require('logging').default;
const ioredis = require("ioredis")
const Areas = require('../global/Areas.js');

class Redis {
    constructor(config) {
        this.logger = createLogger("Redis");
        this.redis = new ioredis(config);

        this.redis.on("ready", async () => {
            this.logger.info("Connected");
            if (database != this) {
                // Use a different database so the dev accounts won't overlap.
                await this.redis.select(1);
            }
            if (process.env.FIRST_WORKER) {
                // Initalization and cache cleanup goes here.
                if (database == this) {
                    this.logger.info("Using Redis as default database.")
                    if (!await this.redis.exists("byonline:globals:userId")) {
                        this.logger.info("Creating userId sequence...");
                        await this.redis.set("byonline:globals:userId", 0);
                    }

                    // Clear out the user list in every area.
                    const keys = [];
                    for (const areaId of Object.keys(Areas.Areas)) {
                        keys.push(`byonline:areas:football:${areaId}`,
                                  `byonline:areas:baseball:${areaId}`);
                    }
                    this.redis.del(keys);
                } else {
                    // Flush the entire cache and start off clean.
                    await this.redis.flushdb();
                }
            }
        });
    }

    async getUserById(userId, game) {
        const response = await this.redis.hgetall(`byonline:users:${userId}`);
        if (Object.keys(response).length == 0) {
            this.logger.warn(`User ${userId} not found in Redis!`);
            return {};
        }
	let stats;
        if (database == this) {
            stats = (game == 'football' ? response['f_stats'] : response['b_stats']);
        } else {
            stats = response['stats'];
        }
        return {
            'id': Number(userId),
            'user': response['user'],
            'icon': Number(response['icon']),
            'stats': stats
            .split(',').map(Number),
            'game': response['game'],
            'area': Number(response['area']),
            'inGame': Number(response['inGame']),
            'phone': Number(response['phone']),
            'opponent': Number(response['opponent'])
        }
    }

    async getUserByName(username) {
        const userId = await this.redis.hget("byonline:users:nameToId", username);
        if (userId) {
            return await this.getUserById(userId);
        }
        return undefined;
    }

    async addUser(userId, user, game) {
        // Add some server specific keys.
        user.game = game;
        user.area = 0;
        user.phone = 0;
        user.opponent = 0;
        user.inGame = 0;

        await this.redis.hmset(`byonline:users:${userId}`, user);
        await this.redis.hset("byonline:users:nameToId", user['user'].toUpperCase(), userId);
    }

    async getUser(username, password, game) {
        if (database != this) {
            this.logger.warn("Redis isn't set as default database, calling getUser shouldn't be possible");
            return {error: 1, message: "Internal error."};
        }
        let user = await this.getUserByName(username);
        if (user) {
            await this.addUser(user.id, user, game)
            return user;
        } else {
            const userId = await this.redis.incr("byonline:globals:userId")
            user = {
                'user': username,
                'icon': 0,
                'f_stats': Array(42).fill(0),
                'b_stats': Array(29).fill(0),
            }
            this.addUser(userId, user, game);
            user['id'] = userId;
            return user;
        }
    }

    async getUserWithToken(token, game) {
        return {error: 1, message: "Redis does not support token logins."};
    }

    async removeUser(userId, game) {
        // We don't want to remove users from a dev database.
        if (database != this) {
            // We need the name to clear the nameToId from.
            const user = await this.getUserById(userId, game);
            if (Object.keys(user).length == 0)
                return;

            await this.redis.del(`byonline:users:${userId}`);
            await this.redis.hdel('byonline:users:nameToId', user.user.toUpperCase());
        } else {
            await this.redis.hmset(`byonline:users:${userId}`, {
                'game': '',
                'area': 0,
                'phone': 0,
                'opponent': 0
            });
        }

        await this.removeOngoingResults(userId, game);
    }

    async setIcon(userId, icon) {
        await this.redis.hset(`byonline:users:${userId}`, 'icon', icon);
    }

    async getUserIdsInArea(areaId, game) {
        return await this.redis.lrange(`byonline:areas:${game}:${areaId}`, 0, -1)
        .then((users) => {
            return users.map(Number);
        });
    }

    async getUsersInArea(areaId, game) {
        const usersList = await this.getUserIdsInArea(areaId, game);
        const users = [];
        for (const userId of usersList) {
            const user = await this.getUserById(userId);
            // If the user doesn't exist or in a game, skip them out.
            if (Object.keys(user).length == 0 || user.inGame)
                continue;
            users.push(user);
        }
        return users;
    }

    async addUserToArea(userId, areaId, game) {
        if (await this.redis.lpos(`byonline:areas:${game}:${areaId}`, userId) == null) {
            await this.redis.rpush(`byonline:areas:${game}:${areaId}`, userId);
            await this.redis.hset(`byonline:users:${userId}`, {area: areaId});
        }
        // This calls sendUsersInArea
        await this.setPhoneStatus(userId, areaId, game, 0);
        // TODO: Only send games playing to this specific user.
        await this.sendGamesPlayingInArea(areaId, game);
    }

    async removeUserFromArea(userId, areaId, game) {
        await this.redis.lrem(`byonline:areas:${game}:${areaId}`, 0, userId);
        await this.redis.hset(`byonline:users:${userId}`, {area: 0});
        await this.sendUsersInArea(areaId, game);
        await this.sendGamesPlayingInArea(areaId, game);

    }

    async sendUsersInArea(areaId, game) {
        const users = await this.getUsersInArea(areaId, game);
        process.send({cmd: 'update_players_list',
                      area: areaId,
                      game: game,
                      users: users
        });
    }

    async setPhoneStatus(userId, areaId, game, phoneStatus) {
        await this.redis.hset(`byonline:users:${userId}`, {phone: phoneStatus});
        // Update the clients in area.
        await this.sendUsersInArea(areaId, game);
    }

    async setInGame(userId, inGame) {
        await this.redis.hset(`byonline:users:${userId}`, {inGame: inGame});
    }

    async sendGamesPlayingInArea(areaId, game) {
        const usersList = await this.getUserIdsInArea(areaId, game);
        let gamesPlaying = 0;
        for (const userId of usersList) {
            const user = await this.getUserById(userId);
            if (user.inGame) {
                gamesPlaying += .5;
            }
        }
        process.send({cmd: "update_games_playing",
                      area: areaId,
                      game: game,
                      games: Math.floor(gamesPlaying)
        });
    }

    async setOngoingResults(userId, game, ongoingResults) {
        await this.redis.hmset(`byonline:ongoingResults:${game}:${userId}`, ongoingResults);
    }

    async getOngoingResults(userId, game) {
        const ongoingResults = await this.redis.hgetall(`byonline:ongoingResults:${game}:${userId}`);
        return ongoingResults;
    }

    async removeOngoingResults(userId, game) {
        const resultsKey = `byonline:ongoingResults:${game}:${userId}`;
        if (await this.redis.exists(resultsKey)) {
            await this.redis.del(resultsKey);
        }
    }

    async getTeam(userId, game) {
        return {error: 1, message: "Redis API does not support teams"};
    }
}

module.exports = Redis;
