package main

import (
	"fmt"
	"os"

	"github.com/joho/godotenv"
)

// Config holds all configuration for the application.
type Config struct {
	MinioEndpoint  string
	MinioAccessKey string
	MinioSecretKey string
	MinioBucket    string
	ServerPort     string
}

// LoadConfig populates a Config struct from environment variables,
// loading from a .env file as a fallback for local development.
func LoadConfig() (*Config, error) {
	// Attempt to load .env file. This is not an error if it doesn't exist.
	_ = godotenv.Load()

	cfg := &Config{
		MinioEndpoint:  os.Getenv("MINIO_ENDPOINT"),
		MinioAccessKey: os.Getenv("MINIO_ACCESS_KEY"),
		MinioSecretKey: os.Getenv("MINIO_SECRET_KEY"),
		MinioBucket:    os.Getenv("MINIO_BUCKET_NAME"),
		ServerPort:     os.Getenv("SERVER_PORT"),
	}

	// Validate required fields
	if cfg.MinioEndpoint == "" || cfg.MinioAccessKey == "" || cfg.MinioSecretKey == "" || cfg.MinioBucket == "" {
		return nil, fmt.Errorf("MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, and MINIO_BUCKET_NAME must be set")
	}

	if cfg.ServerPort == "" {
		cfg.ServerPort = "3000" // Default port
	}

	return cfg, nil
}
