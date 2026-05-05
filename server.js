const express = require("express");
const mysql = require("mysql2");
const cors = require("cors");
const path = require("path");
const http = require("http");
const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname)));

const db = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: "roni1234",
    database: "testi"
});

db.connect(function(err) {
    if (err) throw err;
    console.log("MySQL connected");
});

app.post("/login", function(req, res) {
    const user = req.body.user;
    const password = req.body.password;

    const checkSql = "SELECT * FROM users WHERE user = ? AND password = ?";

    db.query(checkSql, [user, password], function(err, result) {
        if (err) {
            res.status(500).json({ status: "error", message: "Tietokantavirhe" });
            return;
        }

        if (result.length > 0) {
            res.json({ status: "ok", message: "Kirjautuminen onnistui" });
        } else {
            res.status(401).json({ status: "error", message: "Väärä käyttäjänimi tai salasana" });
        }
    });
});

function proxyToFlask(req, res, flaskEndpoint) {
    const options = {
        hostname: 'localhost',
        port: 5000,
        path: flaskEndpoint,
        method: req.method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    const flaskReq = http.request(options, function(flaskRes) {
        let data = '';
        flaskRes.on('data', function(chunk) {
            data += chunk;
        });
        flaskRes.on('end', function() {
            res.status(flaskRes.statusCode).json(JSON.parse(data));
        });
    });

    flaskReq.on('error', function(e) {
        console.error('Flask connection error:', e);
        res.status(500).json({ status: 'error', message: 'Flask server unavailable' });
    });

    flaskReq.write(JSON.stringify(req.body));
    flaskReq.end();
}

app.post("/api/game/create", function(req, res) {
    proxyToFlask(req, res, '/api/game/create');
});

app.post("/api/game/round", function(req, res) {
    proxyToFlask(req, res, '/api/game/round');
});

app.post("/api/game/travel", function(req, res) {
    proxyToFlask(req, res, '/api/game/travel');
});

app.post("/api/game/event", function(req, res) {
    proxyToFlask(req, res, '/api/game/event');
});

app.post("/api/game/check-victory", function(req, res) {
    proxyToFlask(req, res, '/api/game/check-victory');
});

app.listen(3000, function() {
    console.log("Server running on port 3000");
});