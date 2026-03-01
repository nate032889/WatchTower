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

// LoadConfig populates a Config struct from environment variables.
// It loads from .env.local if it exists, otherwise it falls back to .env.
func LoadConfig() (*Config, error) {
	// Use .env.local if it exists, otherwise use .env
	envFile := ".env.local"
	if _, err := os.Stat(envFile); os.IsNotExist(err) {
		envFile = ".env"
	}

	// godotenv.Load will not override existing system environment variables.
	_ = godotenv.Load(envFile)

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
