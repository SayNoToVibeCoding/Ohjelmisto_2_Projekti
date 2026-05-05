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
        
        game = SpaceGame(db_config)
        game.player_name = player_name
        game.create_game()
        
        games[player_name] = game
        
        return jsonify({
            'status': 'ok',
            'game_id': game.game_id,
            'fuel': game.fuel,
            'resources': game.resources
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


if __name__ == '__main__':
    app.run(debug=True, port=5000)
