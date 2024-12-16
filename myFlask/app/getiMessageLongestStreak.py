import sqlite3
from datetime import datetime, timedelta
import pytz

from app.config import DB_PATH

# Define US CST timezone
CST = pytz.timezone("America/Chicago")

def getiMessageLongestStreakFunc(db_path):
    """
    Analyze iMessage logs to find the longest message streaks for each contact.
    
    Args:
        db_path (str): Path to the SQLite database
    
    Returns:
        List of tuples: (contactName, longest_streak_days, streak_start_date, streak_end_date, is_current)
    """
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to get all messages ordered by contact and timestamp
    query = """
    SELECT contactName, secondsSinceEpoch 
    FROM imessages 
    WHERE contactName IS NOT NULL 
    ORDER BY contactName, secondsSinceEpoch
    """
    cursor.execute(query)
    messages = cursor.fetchall()
    conn.close()

    # Function to convert seconds since epoch to datetime in US CST
    def seconds_to_datetime_cst(seconds):
        return datetime.fromtimestamp(seconds, pytz.UTC).astimezone(CST)

    # Analyze streaks for each contact
    contact_streaks = {}

    for contact in set(msg[0] for msg in messages):
        # Get all timestamps for this contact
        contact_timestamps = [msg[1] for msg in messages if msg[0] == contact]
        contact_timestamps.sort()

        # Convert timestamps to CST datetime objects
        contact_datetimes = [seconds_to_datetime_cst(ts) for ts in contact_timestamps]

        # Track streaks
        max_streak_days = 0
        max_streak_start = None
        max_streak_end = None
        current_streak_start = contact_datetimes[0]
        current_streak_end = current_streak_start

        for i in range(1, len(contact_datetimes)):
            prev_time = contact_datetimes[i - 1]
            curr_time = contact_datetimes[i]

            # Check if this message is within 24 hours of the previous message
            if (curr_time.date() - prev_time.date()) <= timedelta(days=1):
                # Extend current streak
                current_streak_end = curr_time
            else:
                # Streak broken, calculate streak length
                streak_days = (current_streak_end.date() - current_streak_start.date()).days + 1
                if streak_days > max_streak_days:
                    max_streak_days = streak_days
                    max_streak_start = current_streak_start
                    max_streak_end = current_streak_end

                # Reset current streak
                current_streak_start = curr_time
                current_streak_end = curr_time

        # Handle final streak at the end of the loop
        streak_days = (current_streak_end.date() - current_streak_start.date()).days + 1
        if streak_days > max_streak_days:
            max_streak_days = streak_days
            max_streak_start = current_streak_start
            max_streak_end = current_streak_end

        # Determine if the streak is current (ends today in CST)
        today_cst = datetime.now(pytz.UTC).astimezone(CST).date()
        is_current = max_streak_end.date() == today_cst

        # Add the longest streak for this contact
        contact_streaks[contact] = {
            'longest_streak': max_streak_days,
            'streak_start': max_streak_start,
            'streak_end': max_streak_end,
            'is_current': is_current
        }

    # Prepare final result list
    result = [
        (
            contact,
            info['longest_streak'],
            info['streak_start'].strftime('%d-%m-%Y'),
            info['streak_end'].strftime('%d-%m-%Y'),
            info['is_current']
        )
        for contact, info in contact_streaks.items()
    ]

    # Sort by longest streak in descending order
    result.sort(key=lambda x: x[1], reverse=True)

    return result

# Example usage
if __name__ == "__main__":
    streaks = getiMessageLongestStreakFunc(DB_PATH)
    for streak in streaks:
        print(f"Contact: {streak[0]}")
        print(f"Longest Streak: {streak[1]} days")
        print(f"Streak Start: {streak[2]}")
        print(f"Streak End: {streak[3]}")
        print(f"Currently Active: {streak[4]}")
        print("---")
