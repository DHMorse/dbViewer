package app

import "fmt"

func GetDiscordStatsFunc() interface{} {
	fmt.Println("Calling GetDiscordStatsFunc...")
	return "Discord Stats Placeholder"
}

func GetLongestDiscordStreakFunc() interface{} {
	fmt.Println("Calling GetLongestDiscordStreakFunc...")
	return "Discord Longest Streak Placeholder"
}

func GetiMessageStatsFunc(dbPath string) interface{} {
	fmt.Printf("Calling GetiMessageStatsFunc with DB Path: %s\n", dbPath)
	return "iMessage Stats Placeholder"
}

func GetiMessageLongestStreakFunc(dbPath string) interface{} {
	fmt.Printf("Calling GetiMessageLongestStreakFunc with DB Path: %s\n", dbPath)
	return "iMessage Longest Streak Placeholder"
}

func GetiMessageCurrentStreakFunc(dbPath string) interface{} {
	fmt.Printf("Calling GetiMessageCurrentStreakFunc with DB Path: %s\n", dbPath)
	return "iMessage Current Streak Placeholder"
}
