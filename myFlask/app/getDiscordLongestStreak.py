from datetime import datetime, timedelta
from pytz import timezone
from app.config import getDbConnection

def getLongestDiscordStreakFunc():
    conn = getDbConnection()
    cursor = conn.cursor()
    
    # Get unique usernames
    cursor.execute("SELECT DISTINCT username FROM messages")
    usernames = [row[0] for row in cursor.fetchall()]
    
    # Track and find streaks
    streak_data = []
    today = datetime.now(timezone('US/Central')).date()  # Today's date in CST
    
    # Define timezones
    utc_tz = timezone('UTC')
    cst_tz = timezone('US/Central')
    
    for username in usernames:
        # Query to get sorted unique dates for the user in UTC
        query = """
        SELECT DISTINCT DATE(time) as message_date
        FROM messages
        WHERE username = %s
        ORDER BY message_date
        """
        cursor.execute(query, (username,))
        
        # Convert UTC dates to CST dates
        date_list = [utc_tz.localize(datetime.combine(row[0], datetime.min.time())).astimezone(cst_tz).date() 
                     for row in cursor.fetchall()]
        
        if not date_list:
            streak_data.append((username, 0, None, None, False))
            continue
        
        # Streak calculation logic
        longest_streak = 1
        current_streak = 1
        streak_start = date_list[0]
        longest_start = longest_end = streak_start
        
        for i in range(1, len(date_list)):
            if date_list[i] - date_list[i-1] == timedelta(days=1):
                current_streak += 1
            else:
                if current_streak > longest_streak:
                    longest_streak = current_streak
                    longest_start = streak_start
                    longest_end = date_list[i-1]
                current_streak = 1
                streak_start = date_list[i]
        
        # Final streak check
        if current_streak > longest_streak:
            longest_streak = current_streak
            longest_start = streak_start
            longest_end = date_list[-1]
        else:
            longest_end = longest_end  # Retain the end of the longest streak
        
        # Check if the longest streak is current
        is_current_streak = longest_end == today
        streak_data.append((username, longest_streak, longest_start, longest_end, is_current_streak))
    
    conn.close()
    return sorted(streak_data, key=lambda x: x[1], reverse=True)