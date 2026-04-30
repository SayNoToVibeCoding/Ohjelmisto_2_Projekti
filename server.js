const express = require("express");
const mysql = require("mysql2");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

const db = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: "ahmed12345",
    database: "game"
});

db.connect(err => {
    if (err) throw err;
    console.log("MySQL connected");
});

app.post("/login", (req, res) => {
    const { user, password } = req.body;

    const sql = "INSERT INTO users (user, password) VALUES (?, ?)";

    db.query(sql, [user, password], (err, result) => {
        if (err) throw err;
        res.send("Saved");
    });
});

app.listen(3000, () => console.log("Server running on port 3000"));