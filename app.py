from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

# Initialize Flask app
app = Flask(__name__)

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'         # Default MySQL server
app.config['MYSQL_USER'] = 'root'              # Default MySQL username (commonly 'root')
app.config['MYSQL_PASSWORD'] = ''              # Leave blank if no password
app.config['MYSQL_DB'] = 'restful_web_service' # Use the exact name of your database

# Configure JWT
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Replace with a secure secret key
jwt = JWTManager(app)

# Initialize MySQL
mysql = MySQL(app)

# Route to populate the database
@app.route('/populate', methods=['POST'])
def populate_database():
    try:
        cur = mysql.connection.cursor()
        # Sample data for the movies table
        sample_data = [
            ('The Shawshank Redemption', 'Frank Darabont', 1994),
            ('The Godfather', 'Francis Ford Coppola', 1972),
            ('The Dark Knight', 'Christopher Nolan', 2008),
            ('Pulp Fiction', 'Quentin Tarantino', 1994),
            ('The Lord of the Rings: The Return of the King', 'Peter Jackson', 2003)
        ]
        cur.executemany("INSERT INTO movies (title, director, year) VALUES (%s, %s, %s)", sample_data)
        mysql.connection.commit()
        return jsonify({"message": "Database populated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to fetch all movies
@app.route('/movies', methods=['GET'])
@jwt_required()
def get_movies():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM movies")
        movies = cur.fetchall()
        # Transform data into JSON format
        movies_list = [
            {"id": row[0], "title": row[1], "director": row[2], "year": row[3]}
            for row in movies
        ]
        return jsonify(movies_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to fetch a single movie by ID
@app.route('/movies/<int:movie_id>', methods=['GET'])
@jwt_required()
def get_movie_by_id(movie_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
        movie = cur.fetchone()
        if not movie:
            return jsonify({"message": "Movie not found"}), 404
        movie_data = {"id": movie[0], "title": movie[1], "director": movie[2], "year": movie[3]}
        return jsonify(movie_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to add a new movie
@app.route('/movies', methods=['POST'])
@jwt_required()
def add_movie():
    try:
        data = request.get_json()
        title = data['title']
        director = data['director']
        year = data['year']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO movies (title, director, year) VALUES (%s, %s, %s)", (title, director, year))
        mysql.connection.commit()
        return jsonify({"message": "Movie added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to update a movie by ID
@app.route('/movies/<int:movie_id>', methods=['PUT'])
@jwt_required()
def update_movie(movie_id):
    try:
        data = request.get_json()
        title = data.get('title')
        director = data.get('director')
        year = data.get('year')

        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE movies SET title = %s, director = %s, year = %s WHERE id = %s",
            (title, director, year, movie_id)
        )
        mysql.connection.commit()

        if cur.rowcount == 0:
            return jsonify({"message": "Movie not found"}), 404

        return jsonify({"message": "Movie updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to delete a movie by ID
@app.route('/movies/<int:movie_id>', methods=['DELETE'])
@jwt_required()
def delete_movie(movie_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM movies WHERE id = %s", (movie_id,))
        mysql.connection.commit()

        if cur.rowcount == 0:
            return jsonify({"message": "Movie not found"}), 404

        return jsonify({"message": "Movie deleted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to authenticate and generate JWT
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        if not user:
            return jsonify({"message": "Invalid credentials"}), 401

        access_token = create_access_token(identity=username)
        return jsonify({"access_token": access_token})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to register a new user
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()

        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Debugging: Print all routes
print(app.url_map)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
