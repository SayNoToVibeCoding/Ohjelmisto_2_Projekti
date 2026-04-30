from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

from game_logic import SpaceGame

app = Flask(__name__)
CORS(app)

db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "roni1234",
    "database": "testi",
    "port": 3306,
}

try:
    db = mysql.connector.connect(**db_config)
    db_cursor = db.cursor(dictionary=True)
    print("Connected to MySQL")
except Error as e:
    db = None
    db_cursor = None
    print(f"Error connecting to MySQL: {e}")

game = SpaceGame(db_config)


@app.get("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Space Game API is running"
    })


@app.get("/api/db-test")
def db_test():
    if db_cursor is None:
        return jsonify({
            "status": "error",
            "message": "Database connection not available"
        }), 500

    try:
        db_cursor.execute("SELECT 1 AS test")
        result = db_cursor.fetchone()
        return jsonify({
            "status": "ok",
            "result": result
        })
    except Error as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.post("/api/game/start")
def start_game():
    data = request.get_json(silent=True) or {}
    player_name = data.get("player_name", "Player")

    game.player_name = player_name
    game_id = game.create_game()
    planets = game.prepare_planets(game.get_planets())

    return jsonify({
        "status": "ok",
        "message": "Game started",
        "game_id": game_id,
        "state": game.to_dict(),
        "planets": planets
    })


@app.get("/api/game/state")
def game_state():
    return jsonify({
        "status": "ok",
        "state": game.to_dict()
    })


@app.get("/api/game/planets")
def game_planets():
    return jsonify({
        "status": "ok",
        "planets": game.prepare_planets(game.get_planets())
    })


@app.post("/api/game/visit")
def visit_planet():
    data = request.get_json(silent=True) or {}
    planet = data.get("planet")

    if not planet:
        return jsonify({
            "status": "error",
            "message": "No planet provided"
        }), 400

    result = game.visit_planet(planet)

    if result.get("status") != "ok":
        return jsonify(result), 400

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)