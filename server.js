const express = require("express");
const mysql = require("mysql2");
const cors = require("cors");
const path = require("path");
const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname,)));

const db = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: "roni1234",
    database: "testi"
});

db.connect(err => {
    if (err) throw err;
    console.log("MySQL connected");
});

app.post("/login", (req, res) => {
    const user = req.body.user;
    const password = req.body.password;

    const checkSql = "SELECT * FROM users WHERE user = ? AND password = ?";
    

    db.query(checkSql, [user, password], (err, result) => {
        if (err) {
            res.status(500).json({ status: "error", message: "Tietokantavirhe" });
            return;
        }
 
        if (result.length > 0) {
            res.json({ status: "ok", message: "Kirjautuminen onnistui" });
        } 
        else {
            res.status(401).json({ status: "error", message: "Väärä käyttäjänimi tai salasana" });
        }
    });
});


app.listen(3000, () => console.log("Server running on port 3000"));