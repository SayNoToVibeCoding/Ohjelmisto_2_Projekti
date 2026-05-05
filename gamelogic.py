import random
import mysql.connector
from mysql.connector import Error


class SpaceGame:
    def __init__(self, db_config):
        try:
            db_config = dict(db_config)
            db_config['auth_plugin'] = 'mysql_native_password'
            self.db = mysql.connector.connect(**db_config)
            self.cursor = self.db.cursor(dictionary=True)

            self.game_id = None
            self.fuel = 100
            self.max_fuel = 100
            self.round = 1
            self.resources = {'Water': 0, 'Food': 0, 'Technology': 0}
            self.planets_visited = []
            self.player_name = None

        except Error as e:
            print(f"Failed to connect to database: {e}")
            raise

    def to_dict(self):
        return {
            "game_id": self.game_id,
            "fuel": self.fuel,
            "max_fuel": self.max_fuel,
            "round": self.round,
            "resources": self.resources,
            "planets_visited": self.planets_visited,
            "player_name": self.player_name
        }

    def create_game(self):
        try:
            query = """
                INSERT INTO game (co2_consumed, co2_budget, screen_name, location)
                VALUES (0, 100, %s, 'Earth')
            """
            self.cursor.execute(query, (self.player_name,))
            self.db.commit()
            self.game_id = self.cursor.lastrowid

            for resource_name in ['Water', 'Food', 'Technology']:
                self.cursor.execute("SELECT id FROM resource WHERE name = %s", (resource_name,))
                result = self.cursor.fetchone()

                if not result:
                    continue

                self.cursor.execute("""
                    INSERT INTO game_resource (game_id, resource_id, amount)
                    VALUES (%s, %s, 0)
                """, (self.game_id, result['id']))

            self.db.commit()
            return self.game_id
        except Error as e:
            self.db.rollback()
            raise e

    def get_planets(self):
        try:
            query = "SELECT ident, name, elevation_ft FROM airport ORDER BY RAND() LIMIT 5"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error fetching planets: {e}")
            return []

    def prepare_planets(self, planets):
        prepared = []

        for planet in planets:
            prepared.append({
                'ident': planet['ident'],
                'name': planet['name'],
                'elevation': planet['elevation_ft'],
                'fuel_cost': random.randint(5, 30),
                'rewards': {
                    'Water': random.randint(0, 5),
                    'Food': random.randint(0, 5),
                    'Technology': random.randint(0, 5)
                }
            })

        return prepared

    def visit_planet(self, planet):
        fuel_cost = planet.get("fuel_cost", 0)

        if self.fuel < fuel_cost:
            return {
                "status": "error",
                "message": "Not enough fuel"
            }

        self.fuel -= fuel_cost
        self.round += 1
        self.planets_visited.append(planet["ident"])

        rewards = planet.get("rewards", {})
        for key in self.resources:
            self.resources[key] += rewards.get(key, 0)

        return {
            "status": "ok",
            "message": f"Visited {planet['name']}",
            "state": self.to_dict()
        }