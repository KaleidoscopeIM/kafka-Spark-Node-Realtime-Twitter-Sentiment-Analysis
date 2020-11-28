const express = require("express");
const bodyparser = require("body-parser");
const cors = require("cors");
const cron = require("node-cron");
const helmet = require("helmet");
var kafka = require('kafka-node');
const dotenv = require('dotenv');
const app = express();
const http = require('http');
var sockets = new Set();
const host_server = process.env.HOST_SERVER;
const appController = require('./controller.js');

app.use(bodyparser.json());
app.use(bodyparser.urlencoded({ extended: true }));
app.use(helmet()); // securing rest apis
app.use(cors());

const httpServer = http.createServer(app);
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


consumer = consumer.on('message', function(message) {
    console.log(message);
    socket_io_http.emit("message", message.value);
});

app.get("*", (req, res) => {
    // this is default response .. must be in the end of all get requests
    appController.getAll(req, res);

});

let serverInstance = httpServer.listen(process.env.PORT, () => { // run server
    console.log("Express now listening on port :", process.env.PORT);
});