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
        const user = await this.post('/login', {token: this.token,
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
