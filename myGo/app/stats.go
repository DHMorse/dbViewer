package app

import (
	"database/sql"
	"fmt"
	"math"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

// ContactStats represents the statistics for a single contact.
type ContactStats struct {
	Name             string
	TotalMessages    int
	AvgMessagesMonth float64
	AvgMessagesDay   float64
}

func GetDiscordStatsFunc() interface{} {
	fmt.Println("Calling GetDiscordStatsFunc...")
	return "Discord Stats Placeholder"
}

func GetLongestDiscordStreakFunc() interface{} {
	fmt.Println("Calling GetLongestDiscordStreakFunc...")
	return "Discord Longest Streak Placeholder"
}

// GetiMessageStatsFunc calculates message statistics from the SQLite database.
func GetiMessageStatsFunc(dbPath string) ([]ContactStats, error) {
	// Connect to the SQLite database
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %v", err)
	}
	defer db.Close()

	// Query to get message statistics per contact
	query := `
		SELECT 
			contactName, 
			COUNT(*) as total_messages,
			CAST(MIN(secondsSinceEpoch) AS INTEGER) as earliest_timestamp,
			CAST(MAX(secondsSinceEpoch) AS INTEGER) as latest_timestamp
		FROM imessages
		GROUP BY contactName
		ORDER BY total_messages DESC
	`

	// Execute the query
	rows, err := db.Query(query)
	if err != nil {
		return nil, fmt.Errorf("failed to execute query: %v", err)
	}
	defer rows.Close()

	// Process results
	var stats []ContactStats
	for rows.Next() {
		var (
			contactName   string
			totalMessages int
			earliestTS    sql.NullInt64
			latestTS      sql.NullInt64
		)

		// Scan the row data
		err := rows.Scan(&contactName, &totalMessages, &earliestTS, &latestTS)
		if err != nil {
			return nil, fmt.Errorf("failed to scan row: %v", err)
		}

		// Calculate averages
		var avgMsgsMonth, avgMsgsDay float64
		if earliestTS.Valid && latestTS.Valid {
			startDate := time.Unix(earliestTS.Int64, 0)
			endDate := time.Unix(latestTS.Int64, 0)
			totalDays := math.Max(1, float64(endDate.Sub(startDate).Hours()/24)+1)
			totalMonths := math.Max(1, math.Ceil(totalDays/30))

			avgMsgsMonth = float64(totalMessages) / totalMonths
			avgMsgsDay = float64(totalMessages) / totalDays
		}

		// Append to stats
		stats = append(stats, ContactStats{
			Name:             contactName,
			TotalMessages:    totalMessages,
			AvgMessagesMonth: avgMsgsMonth,
			AvgMessagesDay:   avgMsgsDay,
		})
	}

	// Check for any errors during iteration
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("error during row iteration: %v", err)
	}

	return stats, nil
}

func GetiMessageLongestStreakFunc(dbPath string) interface{} {
	fmt.Printf("Calling GetiMessageLongestStreakFunc with DB Path: %s\n", dbPath)
	return "iMessage Longest Streak Placeholder"
}

func GetiMessageCurrentStreakFunc(dbPath string) interface{} {
	fmt.Printf("Calling GetiMessageCurrentStreakFunc with DB Path: %s\n", dbPath)
	return "iMessage Current Streak Placeholder"
}
