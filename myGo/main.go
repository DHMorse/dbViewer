package main

import (
	"fmt"
	"html/template"
	"log"
	"net/http"
	"path/filepath"

	"github.com/DHMorse/dbViewer/m/app"
)

// Define paths
const (
	remoteHost     = "raspberrypi"
	remoteUser     = "danielpi"
	remotePassword = "password"
	remoteFilePath = "/home/danielpi/Documents/httpServer/iMessagelog.db"
	localFilePath  = "./iMessagelog.db" // Adjust for your environment
	templatesDir   = "./templates"
	staticDir      = "./static"
)

func main() {
	// Handle the root route
	http.HandleFunc("/", indexHandler)

	// Serve static files from the static directory
	http.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir(staticDir))))

	// Start the server
	fmt.Println("Server is running on http://localhost:8080")
	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}

// indexHandler handles the root endpoint and renders the template
func indexHandler(w http.ResponseWriter, r *http.Request) {
	// Download the DB file from the remote server
	err := app.DownloadDB(remoteHost, remoteUser, remotePassword, remoteFilePath, localFilePath)
	if err != nil {
		http.Error(w, "Failed to download database file", http.StatusInternalServerError)
		return
	}

	// Placeholder function calls (Replace with actual implementation)
	discordMessageStats := app.GetDiscordStatsFunc()
	discordLongestStreak := app.GetLongestDiscordStreakFunc()
	iMessagePersonData := app.GetiMessageStatsFunc(localFilePath)
	iMessageLongestStreak := app.GetiMessageLongestStreakFunc(localFilePath)
	iMessageCurrentStreak := app.GetiMessageCurrentStreakFunc(localFilePath)

	// Parse HTML template
	tmplPath := filepath.Join(templatesDir, "index.html")
	tmpl, err := template.ParseFiles(tmplPath)
	if err != nil {
		http.Error(w, "Failed to load template", http.StatusInternalServerError)
		return
	}

	// Data to pass to the template
	data := struct {
		DiscordMessageStats   interface{}
		DiscordLongestStreak  interface{}
		IMessagePersonData    interface{}
		IMessageLongestStreak interface{}
		IMessageCurrentStreak interface{}
	}{
		DiscordMessageStats:   discordMessageStats,
		DiscordLongestStreak:  discordLongestStreak,
		IMessagePersonData:    iMessagePersonData,
		IMessageLongestStreak: iMessageLongestStreak,
		IMessageCurrentStreak: iMessageCurrentStreak,
	}

	// Render the template with data
	if err := tmpl.Execute(w, data); err != nil {
		http.Error(w, "Failed to render template", http.StatusInternalServerError)
	}
}
