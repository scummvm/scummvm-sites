"use strict";
const createLogger = require('logging').default;

class NetworkConnection {
    constructor(socket) {
        this.socket = socket;
        this.logger = createLogger(socket.remoteAddress + ':' + socket.remotePort)
        this.terminated = false;
        this.buffer = '';

        this.userId = 0;
        this.game = '';
        this.version = '';

        this.areaId = 0;

        this.sliceStart = 0;
        this.sliceEnd = 0;

        this.opponentId = 0;

        this.receivedHeartbeat = true;
        this.heartbeatTimer = setTimeout(() => {
            if (this.terminated) return;
            if (this.receivedHeartbeat) {
                this.send("heartbeat");
                this.receivedHeartbeat = false;
                this.heartbeatTimer.refresh();
            } else {
                this.kick(1, "Heartbeat timeout.");
            }
        }, 30 * 1000);

        this.socket.on('close', (hadError) => {
            if (this.terminated) return;
            this.logger.debug("Connection closed");
            server.handleDisconnect(this, true);
        });

        this.socket.on('error', (error) => {
            if (this.terminated) return;
            this.logger.error(`Error on connection ${this.socket.remoteAddress}:${this.socket.remotePort}.`, error);
            // 'close' event emits after.
        });

        this.socket.on('data', (data) => {
            if (this.terminated) return;
            this.buffer += data;
            if (this.buffer.includes('\n')) {
                const messages = this.buffer.split('\n');
                // Reset the buffer
                this.buffer = messages.pop();

                for (const message of messages) {
                    let json;
                    try {
                        json = JSON.parse(message)
                    } catch (e) {
                        this.logger.error("Received trunciated data!")
                        continue;
                    }

                    const command = json.cmd;
                    if (!command) {
                        this.logger.warn("Received data without command value!")
                        continue;
                    }
                    delete json.cmd;
                    this.logger.debug(`Received "${command}" message:`, json);

                    if (command in server.messages) {
                        server.messages[command](this, json);
                    } else {
                        this.logger.error("Got unknown message:", {command});
                    }
                }
            }
        });
    }

    send(command, object = {}) {
        if (this.terminated) return;
        object.cmd = command;
        const json = JSON.stringify(object);
        this.logger.debug("Writing to connection:", json);
        this.socket.write(json + "\n");
    }

    kick(type, reason) {
        if (this.terminated) return;
        this.logger.warn("Kicking:", reason);
        this.send("disconnect", {"type": type, "message": reason});
        server.handleDisconnect(this);
    }
}

module.exports = NetworkConnection;
