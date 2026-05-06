from flask import Flask, render_template, request, jsonify, send_file
from Space_Game import SpaceGame
import mysql.connector
from mysql.connector import Error
import json

app = Flask(__name__, static_folder='.', static_url_path='')
games = {}

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'roni1234',
    'database': 'testi',
    'auth_plugin': 'mysql_native_password'
}

def load_player_state(player_name):
    db = get_db_connection()
    if not db:
        return None
    try:
        cur = db.cursor(dictionary=True)
        cur.execute("""
            SELECT fuel, water, food, technology, level
            FROM player
            WHERE name=%s
            LIMIT 1
        """, (player_name,))
        row = cur.fetchone()
        cur.close()
        db.close()
        return row
    except Error as e:
        print(f"load_player_state error: {e}")
        try:
            db.close()
        except Exception:
            pass
        return None

def save_player_state(player_name, fuel, resources, planets_visited_count):
    db = get_db_connection()
    if not db:
        return
    try:
        cur = db.cursor()
        # ensure player row exists
        cur.execute("INSERT IGNORE INTO player (name) VALUES (%s)", (player_name,))
        cur.execute("""
            UPDATE player
            SET fuel=%s, water=%s, food=%s, technology=%s, level=%s
            WHERE name=%s
        """, (
            int(fuel),
            int(resources.get("Water", 0)),
            int(resources.get("Food", 0)),
            int(resources.get("Technology", 0)),
            int(planets_visited_count),
            player_name
        ))
        db.commit()
        cur.close()
        db.close()
    except Error as e:
        print(f"save_player_state error: {e}")
        try:
            db.rollback()
            db.close()
        except Exception:
            pass

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def index():
    return send_file('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            user = request.json.get('user')
            password = request.json.get('password')
        else:
            user = request.form.get('user')
            password = request.form.get('password')
        
        print(f"Login attempt: user={user}, password={password}")
        
        try:
            db = get_db_connection()
            if not db:
                return jsonify({'status': 'error', 'message': 'Tietokantavirhe'}), 500
            
            cursor = db.cursor(dictionary=True)
            
            # Tarkista käyttäjä tietokannasta
            sql = "SELECT * FROM users WHERE user = %s AND password = %s"
            cursor.execute(sql, (user, password))
            result = cursor.fetchone()
            
            print(f"Database result: {result}")
            
            cursor.close()
            db.close()
            
            if result:
                return jsonify({'status': 'ok', 'message': 'Kirjautuminen onnistui'})
            else:
                return jsonify({'status': 'error', 'message': 'Väärä käyttäjänimi tai salasana'}), 401
                
        except Error as e:
            print(f"Database error: {e}")
            return jsonify({'status': 'error', 'message': f'Tietokantavirhe: {str(e)}'}), 500
    
    return send_file('login.html')

@app.route('/Pelihtml.html')
def game_page():
    return send_file('Pelihtml.html')

@app.route('/api/game/create', methods=['POST'])
def create_game():
    try:
        player_name = request.json.get('player_name')

        # If game already in memory, return it
        game = games.get(player_name)
        if game:
            return jsonify({
                'status': 'ok',
                'game_id': game.game_id,
                'fuel': game.fuel,
                'resources': game.resources,
                'planets_visited': game.planets_visited
            })

        # Create a new in-memory game object
        game = SpaceGame(db_config)
        game.player_name = player_name

        # Load saved state from DB (player table)
        state = load_player_state(player_name)
        if state and not (
            (state.get("fuel") in (None, 100)) and
            (state.get("water") in (None, 0)) and
            (state.get("food") in (None, 0)) and
            (state.get("technology") in (None, 0)) and
            (state.get("level") in (None, 0, 1))
        ):
            game.fuel = int(state.get("fuel") or 100)
            game.resources["Water"] = int(state.get("water") or 0)
            game.resources["Food"] = int(state.get("food") or 0)
            game.resources["Technology"] = int(state.get("technology") or 0)

            visited = int(state.get("level") or 0)
            game.planets_visited = [None] * visited
        else:
            # No usable save -> start fresh (DON'T call game.create_game() to avoid game.id error)
            game.fuel = 100
            game.resources = {"Water": 0, "Food": 0, "Technology": 0}
            game.planets_visited = []

            # and persist initial state so next time we can load it
            save_player_state(player_name, game.fuel, game.resources, len(game.planets_visited))

        games[player_name] = game

        return jsonify({
            'status': 'ok',
            'game_id': game.game_id,
            'fuel': game.fuel,
            'resources': game.resources,
            'planets_visited': game.planets_visited
        })

    except Exception as e:
        print(f"Create game error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/game/round', methods=['POST'])
def get_round():
    try:
        player_name = request.json.get('player_name')
        game = games.get(player_name)
        
        if not game:
            return jsonify({'status': 'error', 'message': 'Game not found'}), 404
        
        planets = game.get_planets()
        planets_data = game.prepare_planets(planets)
        
        return jsonify({
            'status': 'ok',
            'round': game.round,
            'fuel': game.fuel,
            'resources': game.resources,
            'planets': planets_data
        })
    except Exception as e:
        print(f"Get round error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/game/travel', methods=['POST'])
def travel():
    try:
        player_name = request.json.get('player_name')
        planet = request.json.get('planet')
        
        game = games.get(player_name)
        
        if not game:
            return jsonify({'status': 'error', 'message': 'Game not found'}), 404
        
        result = game.travel_to(planet)
        
        if not result:
            return jsonify({'status': 'error', 'message': 'Not enough fuel'})
        
        return jsonify({
            'status': 'ok',
            'fuel': game.fuel,
            'resources': game.resources,
            'planets_visited': game.planets_visited
        })
    except Exception as e:
        print(f"Travel error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/game/event', methods=['POST'])
def event():
    try:
        player_name = request.json.get('player_name')
        game = games.get(player_name)
        
        if not game:
            return jsonify({'status': 'error', 'message': 'Game not found'}), 404
        
        roll = game.random_event()
        
        return jsonify({
            'status': 'ok',
            'roll': roll,
            'fuel': game.fuel
        })
    except Exception as e:
        print(f"Event error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/game/check-victory', methods=['POST'])
def check_victory():
    try:
        player_name = request.json.get('player_name')
        game = games.get(player_name)
        
        if not game:
            return jsonify({'status': 'error', 'message': 'Game not found'}), 404
        
        victory = game.check_victory()
        
        return jsonify({
            'status': 'ok',
            'victory': victory,
            'fuel': game.fuel,
            'resources': game.resources
        })
    except Exception as e:
        print(f"Check victory error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


#endscreen
@app.route('/api/game/status', methods=['POST'])
def game_status():
    try:
        player_name = request.json.get('player_name')
        game = games.get(player_name)

        if not game:
            return jsonify({'status': 'error', 'message': 'Game not found'}), 404

        victory = game.check_victory()
        out_of_fuel = game.fuel <= 0

        ended = victory or out_of_fuel

        reason = None
        if victory:
            reason = 'victory'
        elif out_of_fuel:
            reason = 'fuel'

        return jsonify({
            'status': 'ok',
            'ended': ended,
            'reason': reason,
            'round': game.round,
            'fuel': game.fuel,
            'resources': game.resources,
            'planets_visited': game.planets_visited
        })
    except Exception as e:
        print(f"Game status error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/game/reset', methods=['POST'])
def reset_game():
    try:
        player_name = request.json.get('player_name')

        # remove in-memory game
        if player_name in games:
            del games[player_name]

        # reset DB save
        db = get_db_connection()
        if not db:
            return jsonify({'status': 'error', 'message': 'Tietokantavirhe'}), 500

        cur = db.cursor()
        cur.execute("""
            UPDATE player
            SET fuel=100, water=0, food=0, technology=0, level=0
            WHERE name=%s
        """, (player_name,))
        db.commit()
        cur.close()
        db.close()

        return jsonify({'status': 'ok'})
    except Exception as e:
        print(f"Reset game error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
