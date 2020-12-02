const express = require("express");
const bodyparser = require("body-parser");
const cors = require("cors");
const cron = require("node-cron");
const helmet = require("helmet");
var kafka = require('kafka-node');
const dotenv = require('dotenv');
const http = require('http');
var sockets = new Set();
const host_server = process.env.HOST_SERVER;
const appController = require('./controller.js');

const app = express();
const httpServer = http.Server(app);
const socket_io_http = require("socket.io")(httpServer);

dotenv.config();

socket_io_http.on('connection', function(socket) {
    sockets.add(socket);
    console.log("------");
    console.log("New socket connected: ", socket['id']);
    console.log("All connected sockets:", sockets.size);
    let socketArr = Array.from(sockets)
    socketArr.forEach(aSocket => {
        console.log(`${aSocket['id']}`)
    });
    console.log("------");

    socket.on('disconnect', () => {
        console.log("Deleting socket on disconnect: ", socket['id']);
        sockets.delete(socket);
        console.log("Remaining connected sockets: ", sockets.size);
    });
});

let Consumer = kafka.Consumer,
    client = new kafka.KafkaClient(process.env.HOST_SERVER + ":" + process.env.PORT),
    consumer = new Consumer(
        client, [{ topic: 'processedtweets', partition: 0 }], { autoCommit: false });

let Consumer1 = kafka.Consumer,
    client1 = new kafka.KafkaClient(process.env.HOST_SERVER + ":" + process.env.PORT),
    Consumer_sentiments = new Consumer1(
        client1, [{ topic: 'processSentiments', partition: 0 }], { autoCommit: false });

// socket for tweet data delivery to frontend - Gautam Saini
consumer = consumer.on('message', function(message) {
    console.log(message);
    socket_io_http.emit("message", message.value);
});

// socket for sentiment delivery to frontend - Gautam Saini
Consumer_sentiments = Consumer_sentiments.on('message', function(message) {
    console.log(message);
    socket_io_http.emit("sentimet", message.value);
});

app.get("*", (req, res) => {
    // this is default response .. must be in the end of all get requests
    appController.getAll(req, res);
});

let serverInstance = httpServer.listen(process.env.PORT, () => { // run server
    console.log("Express now listening on port :", process.env.PORT);
});