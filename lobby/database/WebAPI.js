"use strict";
const createLogger = require('logging').default;
const bent = require('bent');

class WebAPI {
    constructor(config) {
        this.logger = createLogger('WebAPI');

        this.token = config['token'] || "";

        const endpoint = config['endpoint'];
        this.get = bent(endpoint, 'GET', 'json', 200);
        this.post = bent(endpoint, 'POST', 'json', 200);
    }

    async getUser(username, password, game) {
        // TODO: Replace with /login
        const user = await this.post('/new_login', {token: this.token,
                                                    user: username,
                                                    pass: password,
                                                    game: game});
        if (user.error) {
            return user;
        }
        // Store the user into the Redis cache
        redis.addUser(user.id, {user: user.user,
                                icon: user.icon,
                                stats: user.stats}, game);
        return user;
    }

    async setIcon(userId, icon) {
        const response = await this.post('/set_icon', {token: this.token,
                                                      userId: userId,
                                                      icon: icon});
        if (response.error) {
            this.logger.error("Failed to set icon!", { response });
            return;
        }

        // Set the icon in the Redis cache.
        redis.setIcon(userId, icon);
    }

    async getTeam(userId, game) {
        const response = await this.post('/get_team', {token: this.token,
                                                       userId: userId,
                                                       game: game});
        if (response.error) {
            this.logger.error("Failed to get team!", { response });
        }

        return response;
    }
}

module.exports = WebAPI;
