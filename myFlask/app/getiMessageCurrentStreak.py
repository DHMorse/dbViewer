import sqlite3
from datetime import datetime, timedelta
from typing import List, Tuple
from zoneinfo import ZoneInfo  # Python 3.9+

def getiMessageCurrentStreakFunc(db_path: str) -> List[Tuple[str, int, datetime, datetime, bool]]:
    """
    Calculate message streaks for each contact in the iMessage database, treating all times as CST.
    If the user has not sent a message on the current day, the streak is 0.

    Args:
        db_path (str): Path to the SQLite database
    
    Returns:
        List of tuples containing:
        - Contact name
        - Current streak (days)
        - Streak start date (None if streak is 0)
        - Streak end date (None if streak is 0)
    """
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get unique contacts
    cursor.execute("SELECT DISTINCT contactName FROM imessages")
    contacts = [row[0] for row in cursor.fetchall()]

    # Store streak results
    streak_results = []

    # Define CST timezone
    CST = ZoneInfo("America/Chicago")
    current_date_cst = datetime.now(CST).date()

    for contact in contacts:
        # Fetch all messages for this contact, sorted by secondsSinceEpoch
        cursor.execute("""
            SELECT secondsSinceEpoch 
            FROM imessages 
            WHERE contactName = ? 
            ORDER BY secondsSinceEpoch
        """, (contact,))
        
        timestamps = [row[0] for row in cursor.fetchall()]
        
        # If no messages, skip
        if not timestamps:
            streak_results.append((contact, 0, None, None, False))
            continue

        # Convert timestamps to unique dates in CST
        message_dates = sorted(set(datetime.fromtimestamp(ts, CST).date() for ts in timestamps))

        # If the last message is not today, streak is 0
        if message_dates[-1] != current_date_cst:
            streak_results.append((contact, 0, None, None, False))
            continue

        # Calculate the current streak
        current_streak = 1
        current_streak_start = message_dates[-1]

        for i in range(len(message_dates) - 2, -1, -1):
            # Check if the previous day is exactly 1 day before the current day
            if (current_streak_start - message_dates[i]).days == 1:
                current_streak += 1
                current_streak_start = message_dates[i]
            else:
                break  # Stop counting as the streak is broken

        is_current = False

        if current_streak >= 1:
            is_current = True

        # Append the current streak for this contact
        streak_results.append((contact, current_streak, current_streak_start, current_date_cst, is_current))

    # Close database connection
    conn.close()

    # Sort results by streak length in descending order
    return sorted(streak_results, key=lambda x: x[1], reverse=True)

# Example usage
if __name__ == "__main__":
    db_path = "iMessagelog.db"  # Replace with your actual database path
    streaks = getiMessageCurrentStreakFunc(db_path)
    
    # Print results with formatted dates
    for contact, streak, start, end in streaks:
        if streak == 0:
            print(f"{contact}: {streak} day streak from {start} to {end}")
        else:
            print(f"{contact}: {streak} day streak from {start} to {end}")
