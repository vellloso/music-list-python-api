from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

# Establishing the connection to the MySQL database

connection = mysql.connector.connect(
    host='localhost',
    user='YOUR USER', # EDIT TO YOUR MYSQL USER
    password='YOUR PASSWORD', # EDIT TO YOUR MYSQL PASSWORD
    database='YOUR DATABASE', # EDIT TO YOUR MYSQL USER
)

cursor = connection.cursor()

def create_login_table():
    query = f'SHOW TABLES LIKE "login"'
    cursor.execute(query)
    exists = cursor.fetchone()
    if exists:
        print()
    else:
        query = f"""
        CREATE TABLE login (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(45),
            password VARCHAR(45))
        """
        cursor.execute(query)
        connection.commit()


# Function to display the initial menu and prompt for option selection
def display_menu():
    while True:
        option = input('SELECT AN OPTION: \n\
            (1) Log In\n\
            (2) Sign In\n\
            (3) Quit\n')

        try:
            option = int(option)
        except ValueError:
            print('Select a valid option!\n \n \n')

        if option == 1 or option == 2 or option == 3:
            break
    return option

# Function to retrieve the login table from the database
def get_login_table():
    query = 'SELECT * FROM login'
    cursor.execute(query)
    result = cursor.fetchall()

    logins = []
    for login in result:
        logins.append({
            'id' : login[0],
            'username' : login[1],
            'password' : login[2],
        })

    return logins

# Function for user sign-in
def signin():
    logins = get_login_table()

    while True:
        print('SIGN IN\n\n')
        username = input('Username:\n')
        password = input('Password:\n')

        existing = 0
        for login in logins:
            if login.get('username') == username:
                print('\n User already exists\n')

                existing = 1
                break

        if existing == 0:
            print('Account created successfully!')

            query = f'INSERT INTO login (username, password) VALUES ("{username}", "{password}")'
            cursor.execute(query)
            connection.commit()

            break

    return username

# Function for user login
def login():
    logins = get_login_table()

    while True:
        username = input('Username:\n')
        password = input('Password:\n')

        valid = 0
        for login in logins:
            if login.get('username') == username and login.get('password') == password:
                print('Valid login!')
                valid = 1
                break

        if valid == 1:
            break
        else:
            print('\n Incorrect username or password!!!\n Try again \n')
    return username

# Function to validate user login
def validate_login(username, password):
    logins = get_login_table()
    valid = False
    for login in logins:
        if login.get('username') == username and login.get('password') == password:
            valid = True
            break

    return valid

# Function to check if a user's table exists in the database
def check_user_table(username):
    query = f'SHOW TABLES LIKE "musics_{username}"'
    cursor.execute(query)
    exists = cursor.fetchone()
    if exists:
        return True
    else:
        return False

# Function to create a user's table in the database
def create_user_table(username):
    query = f"""
    CREATE TABLE musics_{username} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        music_title VARCHAR(45),
        music_author VARCHAR(45), 
        music_producer VARCHAR(45)
    )
    """
    cursor.execute(query)
    connection.commit()
    print('Table created successfully')

# Function to define the privacy setting for a user's table
def set_privacy(username):
    while True:
        option = input('\n \n CHOOSE PRIVACY: \n\
            (1) Public (visible to all users) \n\
            (2) Private (visible only to you)\n\
            ')

        try:
            option = int(option)

        except ValueError:
            print('Select a valid option!\n \n \n')

        if option == 1 or option == 2:
            break

    if option == 1:
        query = f'INSERT INTO musics_{username} (music_title, music_author, music_producer) VALUES ("PUBLIC", "PUBLIC", "PUBLIC")'
        cursor.execute(query)
        connection.commit()

    else:
        query = f'INSERT INTO musics_{username} (music_title, music_author, music_producer) VALUES ("PRIVATE", "PRIVATE", "PRIVATE")'
        cursor.execute(query)
        connection.commit()

# Function to display the user interface
def interface():
    create_login_table()
    option = display_menu()

    if option == 1:
        username = login()
        if check_user_table(username) == True:
            print('Table already exists')
        else: 
            create_user_table(username)
            set_privacy(username)

    if option == 2:
        username = signin()
        if check_user_table(username) == True:
            print('Table already exists')
        else: 
            create_user_table(username)
            set_privacy(username)

    else:
        print('')
        username = False

# Function to retrieve a user's table from the database
def get_table(username):
    query = f'SELECT * FROM musics_{username}'
    cursor.execute(query)
    result = cursor.fetchall()

    songs = []
    for song in result:
        songs.append({
            'id' : song[0],
            'music_title' : song[1],
            'music_author' : song[2],
            'music_producer' : song[3],
        })

    return songs

# Endpoint to view other user's songs
@app.route('/musics/<string:username>')
def get_other_user_songs(username):
    songs = get_table(username)
    public = 0
    for song in songs:
        if song.get('music_title') == 'PUBLIC':
            public = 1
            break
    if public == 1:
        return jsonify(songs)
    else:
        return jsonify({'message' : 'SONGS ARE PRIVATE'}), 401



# Endpoint to view user own songs
@app.route('/musics', methods=['GET'])
def get_songs():
    username = request.args.get('username')
    password = request.args.get('password')
    valid = validate_login(username, password)

    if valid:
        songs = get_table(username)
        return jsonify(songs)
    else:
        return jsonify({'message' : 'Invalid login'}), 401

# Endpoint to view user songs separately by id
@app.route('/musics/<int:id>', methods=['GET'])
def get_song_by_id(id):
    username = request.args.get('username')
    password = request.args.get('password')
    valid = validate_login(username, password)

    if valid:
        songs = get_table(username)
        for song in songs:
            if song.get('id') == id:
                return jsonify(song)

    else:
        return jsonify({'message' : 'Invalid login'}), 401

# Endpoit to edit songs based on json
@app.route('/musics/<int:id>', methods=['PUT'])
def edit_song_by_id(id):
    username = request.args.get('username')
    password = request.args.get('password')
    valid = validate_login(username, password)

    if valid:
        edited_song = request.get_json()
        edited_song_id = edited_song.get('id')
        edited_song_title = edited_song.get('music_title')
        edited_song_author = edited_song.get('music_author')
        edited_song_producer = edited_song.get('music_producer')

        songs = get_table(username)
        for song in songs:
            if song.get('id') == id:
                song['music_title'] = edited_song_title
                song['music_author'] = edited_song_author
                song['music_producer'] = edited_song_producer

                query = f"""
                UPDATE musics_{username} 
                SET music_title = '{edited_song_title}',
                    music_author = '{edited_song_author}',
                    music_producer = '{edited_song_producer}'
                WHERE id = {edited_song_id}
                """
                cursor.execute(query)
                connection.commit()
                return jsonify({'message' : 'Song updated successfully'})

        return jsonify({'message' : 'Song not found'}), 404

    else:
        return jsonify({'message' : 'Invalid login'}), 401

# Endpoit to insert new songs based on json


@app.route('/musics', methods=['POST'])
def incluir_nova_musica():
    username = request.args.get('username')
    password = request.args.get('password')
    valid = validate_login(username, password)

    if valid:
        new_song = request.get_json()
        new_song_title = new_song.get('music_title')
        new_song_author = new_song.get('music_author')
        new_song_producer = new_song.get('music_producer')

        comando = f'INSERT INTO musics_{username} (music_title, music_author, music_producer) VALUES ("{new_song_title}", "{new_song_author}", "{new_song_producer}")'
        cursor.execute(comando)
        connection.commit() 
        return jsonify({'message' : 'Song updated successfully'})
    
    else: 
        return jsonify({'mensagem' : 'login invalido'}), 401



# Endpoint to delete songs based on their id
@app.route('/musics/<int:id>', methods=['DELETE'])
def delete_song_by_id(id):
    username = request.args.get('username')
    password = request.args.get('password')
    valid = validate_login(username, password)

    if valid:
        songs = get_table(username)
        for song in songs:
            if song.get('id') == id:
                query = f"DELETE FROM musics_{username} WHERE id = {id}"
                cursor.execute(query)
                connection.commit()
                return jsonify({'message' : 'Song deleted successfully'})

        return jsonify({'message' : 'Song not found'}), 404

    else:
        return jsonify({'message' : 'Invalid login'}), 401


interface()


app.run(port=5000, host='localhost', debug=True)

cursor.close()
connection.close()
