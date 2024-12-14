from flask import Flask, render_template
import paramiko
from scp import SCPClient
import os

from app.getiMessageStats import getiMessageStatsFunc
from app.getDiscordStats import getDiscordStatsFunc
from app.getDiscordLongestStreak import getLongestDiscordStreakFunc

DB_PATH = '/home/daniel/Documents/myCode/dbViewer/myFlask/iMessagelog.db'

# Initialize Flask app
app = Flask(__name__)

def downloadDB(remote_host='raspberrypi', remote_user='danielpi', remote_password='password', remote_file_path='/home/danielpi/Documents/httpServer/iMessagelog.db', local_file_path=DB_PATH):
    try:
        if os.path.exists(local_file_path):
            print(f"Removing existing file: {local_file_path}")
            os.remove(local_file_path)
        # Create an SSH client
        ssh = paramiko.SSHClient()

        # Automatically add host key if not in known_hosts
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the remote host
        ssh.connect(hostname=remote_host, username=remote_user, password=remote_password)

        # Use SCPClient to copy the file
        with SCPClient(ssh.get_transport()) as scp:
            scp.get(remote_file_path, local_file_path)

        print(f"File {remote_file_path} copied to {local_file_path}")

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        # Close the SSH connection
        ssh.close()

# Route for the homepage
@app.route("/")
def index():
    discordStats = getDiscordStatsFunc()
    discordLongestStreak = getLongestDiscordStreakFunc()
    
    downloadDB()
    iMessagePersonData = getiMessageStatsFunc(DB_PATH)
    
    return render_template("index.html", person_data=discordStats, streak_data=discordLongestStreak, iMessagePersonData=iMessagePersonData)

if __name__ == "__main__":
    app.run(debug=True)