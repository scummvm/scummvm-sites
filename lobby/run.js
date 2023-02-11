"use strict"

const yaml         = require('js-yaml');
const fs           = require('fs');
const createLogger = require('logging').default;
const cluster      = require('cluster');

// Read the configuration files.
const config = yaml.load(fs.readFileSync('config.yaml'));

// Get credentials and such from environment variables
const credentials = {
    web: {
        endpoint: process.env.WEB_ENDPOINT,
        token: process.env.WEB_TOKEN,
    },
    redis: {
        host: process.env.REDIS_HOST,
        port: process.env.REDIS_PORT,
    },
    discord: {
        client: process.env.DISCORD_CLIENT,
        token: process.env.DISCORD_TOKEN,
        channel: process.env.DISCORD_CHANNEL,
    }
};

if (cluster.isMaster) {
    // Fork out workers
    for (let i = 0; i < (config['cores'] || 1); i++) {
        const env = {};
        if (i == 0) {
            env.FIRST_WORKER = true;
        }
        const worker = cluster.fork(env);
        worker.on('message', (message) => {
            for (const id in cluster.workers) {
                cluster.workers[id].send(message);
            }
        });
    }
} else {
    // Worker
    const NetworkListener = require('./net/NetworkListener');
    const Redis = require('./database/Redis');
    const Discord = require('./discord/Discord');
    global.server = new NetworkListener(config['network'])
    global.redis = new Redis(credentials.redis);
    if (process.env.DATABASE == 'web') {
        const WebAPI = require('./database/WebAPI');
        global.database = new WebAPI(credentials.web);
    } else {
        global.database = global.redis;
    }

    // Load message functions
    require('./net/DatabaseMessages.js');
    require('./net/AreaMessages.js');
    require('./net/ChallengeMessages.js');
    require('./net/SessionMessages.js');

    if (process.env.FIRST_WORKER && credentials.discord.client) {
      global.discord = new Discord(credentials['discord']);
    }

    // Handle messages from other processes.
    process.on('message', (message) => {
        const cmd = message.cmd;
        delete message.cmd;
        process.emit(cmd, message);
    });
}
