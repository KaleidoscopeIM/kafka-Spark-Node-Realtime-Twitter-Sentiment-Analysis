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

// app.use(bodyparser.json());
// app.use(bodyparser.urlencoded({ extended: true }));
// app.use(helmet()); // securing rest apis
// app.use(cors());

dotenv.config();

// var http = require('http').Server(app);
// var io = require('socket.io')(http);
// var kafka = require('kafka-node');
// var port = 8085;

// var Consumer = kafka.Consumer,
//     client = new kafka.KafkaClient("localhost:9092"),
//     consumer = new Consumer(
//         client, [{ topic: 'processedtweets', partition: 0 }], { autoCommit: false });

// app.get('/', function(req, res) {
//     res.sendfile('index.html');
// });

// socket_io_http.on('connection', function(socket) {
//     console.log('a user connected');
//     socket.on('disconnect', function() {
//         console.log('user disconnected');
//     });
// });

// consumer = consumer.on('message', function(message) {
//     // console.log(message.value);
//     io.emit("message", message.value);
// });

// httpServer.listen(process.env.PORT, function() {
//     console.log("Running on port " + process.env.PORT)
// });






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


consumer = consumer.on('message', function(message) {
    console.log(message);
    socket_io_http.emit("message", message.value);
});

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