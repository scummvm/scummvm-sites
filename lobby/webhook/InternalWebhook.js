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

const express      = require("express");
const bodyParser   = require("body-parser");
const createLogger = require('logging').default;

class InternalWebhook {
    constructor(config) {
        this.logger = createLogger('Webhook');
        this.config = config;
        this.app = express();

        const host = config["host"] || "127.0.0.1";
        const port = Number(config["port"]) || 4000;
        this.token = config["token"] || "";

        this.app.use(bodyParser.json());

        this.app.use((req, res, next) => {
            // Check token.
            if (!this.token || req.body.token == this.token) {
                next();
                return
            }

            res.status(401).json({message: "Invalid token"});
        });

        this.app.listen(port, () => this.logger.info(`Webhook running on ${host} with port ${port}`));

        this.app.post("/ping", (req, res) => {
            res.status(200).json({message: "Pong!"});
        });

        this.app.post("/getUsers", async (req, res) => {
            // This gets the currently logged in users.
            let users = {};
            const userIds = Object.values(await redis.redis.hgetall("byonline:users:nameToId")).map(Number);
            for (const userId of userIds) {
                const user = await redis.getUserById(userId);
                if (Object.keys(user).length == 0 || !user.game)
                  // Not logged in.
                  continue;
                users[userId] = user;
                const ongoingResultsStrings = await redis.getOngoingResults(userId, user.game);
                const ongoingResults = Object.fromEntries(
                    Object.entries(ongoingResultsStrings).map(([k, stat]) => [k, Number(stat)])
                );
                users[userId]["ongoingResults"] = ongoingResults;
            }
            res.status(200).json({users: users})
        });

        this.app.post("/kick/:userId", (req, res) => {
            if (!Number(req.params.userId)) {
                res.status(400).json({message: "Invalid user id"});
                return;
            }

            const reason = req.body.reason || "You have been kicked off the server by an administrator."
            process.send({cmd: 'kick',
                  userId: Number(req.params.userId),
                  type: 901,
                  reason: reason});
            res.status(200).json({message: `Kick request received for user id ${req.params.userId}.`})
        });

        this.app.post("/getGamesEnabled", (req, res) => {
            res.status(200).json({enabled: process.env.DISABLE_NEW_GAMES === "0", message: process.env.DISABLE_NEW_GAMES_REASON || ""});
        });

        this.app.post("/setGamesEnabled", (req, res) => {
            const enabled = req.body.enabled;
            const reason = req.body.message;

            process.env.DISABLE_NEW_GAMES = enabled === true ? "0" : "1";
            process.env.DISABLE_NEW_GAMES_REASON = reason || "";

            res.status(200).json({message: "Updated successfully"});
        });
    }
}

module.exports = InternalWebhook;
