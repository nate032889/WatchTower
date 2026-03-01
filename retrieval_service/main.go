package main

import (
	"log"
	"net/http"

	"github.com/nate/retrieval_service/data"
	"github.com/nate/retrieval_service/service"
)

func main() {
	// 1. Initialize the Data Layer (Repository)
	repo, err := data.NewMinioRepository()
	if err != nil {
		log.Fatalf("FATAL: Could not initialize Minio repository: %v", err)
	}

	// 2. Initialize the Service Layer
	svc := service.NewRetrievalService(repo)

	// 3. Setup Router and Middleware
	r := NewRouter(svc)

	log.Println("Starting retrieval service on :3000...")
	if err := http.ListenAndServe(":3000", r); err != nil {
		log.Fatalf("FATAL: Could not start server: %v", err)
	}
}
