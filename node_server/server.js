const express = require("express");
const bodyparser = require("body-parser");
const cors = require("cors");
const cron = require("node-cron");
const helmet = require("helmet");
var kafka = require('kafka-node');
const dotenv = require('dotenv');
const app = express();

dotenv.config();

app.use(bodyparser.json());
app.use(bodyparser.urlencoded({ extended: true }));
app.use(helmet()); // securing rest apis
app.use(cors());

const server = require("http").createServer(app);

let serverInstance = server.listen(process.env.port, () => { // run server
    console.log("Express now listening on port :", process.env.port);
});