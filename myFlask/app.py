import json
from flask import Flask, render_template
import mysql.connector

# Load database credentials from secrets.json
with open('/home/daniel/Documents/myCode/dbViewer/secrets.json') as f:
    secrets = json.load(f)

app = Flask(__name__)

# Connect to MySQL database
def get_db_connection():
    connection = mysql.connector.connect(
        host=secrets['host'],
        user=secrets['user'],
        password=secrets['password'],
        database=secrets['database']
    )
    return connection

@app.route('/')
def index():
    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Retrieve data from the 'messages' table
    cursor.execute('SELECT * FROM messages')
    messages = cursor.fetchall()

    # Close the connection
    cursor.close()
    connection.close()

    # Render the 'messages.html' template and pass the messages data to it
    return render_template('messages.html', messages=messages)

if __name__ == '__main__':
    app.run(debug=True)
