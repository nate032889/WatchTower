package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/nate032889/WatchTower/intake_service/data"
	"github.com/nate032889/WatchTower/intake_service/service"
)

func main() {
	// 1. Load configuration from environment
	cfg, err := LoadConfig()
	if err != nil {
		log.Fatalf("FATAL: Could not load configuration: %v", err)
	}

	// 2. Initialize the Data Layer with the loaded config
	repo, err := data.NewMinioRepository(
		cfg.MinioEndpoint,
		cfg.MinioAccessKey,
		cfg.MinioSecretKey,
		cfg.MinioBucket,
	)
	if err != nil {
		log.Fatalf("FATAL: Could not initialize Minio repository: %v", err)
	}

	// 3. Initialize the Service Layer
	svc := service.NewIntakeService(repo)

	// 4. Setup Router and Middleware
	r := NewRouter(svc)

	// 5. Start the server
	listenAddr := fmt.Sprintf(":%s", cfg.ServerPort)
	log.Printf("Starting intake service on %s...", listenAddr)
	if err := http.ListenAndServe(listenAddr, r); err != nil {
		log.Fatalf("FATAL: Could not start server: %v", err)
	}
}
