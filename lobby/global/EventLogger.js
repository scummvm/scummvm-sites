"use strict";
const createLogger = require('logging').default;
const logger = createLogger('Event');

const logEvent = (eventName, client, version, additionalData) => {
    const timestamp = new Date().toISOString();
    const eventDesc = Object.assign(
        {
            eventName: eventName,
            timestamp: timestamp,
            user: client.userId,
            version: version || client.version,
            game: client.game,
        },
        additionalData,
    );
    logger.info(JSON.stringify(eventDesc));
};

module.exports = {
    logEvent: logEvent
};
