package service

import (
	"context"
	"fmt"
	"path/filepath"

	"github.com/google/uuid"
	"github.com/nate032889/WatchTower/intake_service/data"
	"github.com/nate032889/WatchTower/intake_service/service/parser"
)

// IntakeService defines the business logic for processing and storing evidence.
type IntakeService interface {
	GetEvidence(ctx context.Context, objectKey string) (string, error)
	ProcessIntake(ctx context.Context, filename string, fileData []byte, contentType string) (string, string, error)
}

type intakeService struct {
	repo data.MinioRepository
}

// NewIntakeService creates a new instance of the intake service.
func NewIntakeService(repo data.MinioRepository) IntakeService {
	return &intakeService{repo: repo}
}

// GetEvidence fetches the object from the repository and parses it.
func (s *intakeService) GetEvidence(ctx context.Context, objectKey string) (string, error) {
	data, err := s.repo.GetObject(ctx, objectKey)
	if err != nil {
		return "", fmt.Errorf("failed to retrieve object '%s': %w", objectKey, err)
	}

	p := parser.GetParser(objectKey)
	parsedContent, err := p.Parse(data)
	if err != nil {
		return "", fmt.Errorf("failed to parse object '%s': %w", objectKey, err)
	}

	return parsedContent, nil
}

// ProcessIntake saves a file to storage and returns the parsed text.
func (s *intakeService) ProcessIntake(ctx context.Context, filename string, fileData []byte, contentType string) (string, string, error) {
	ext := filepath.Ext(filename)
	objectKey := fmt.Sprintf("%s%s", uuid.New().String(), ext)

	if err := s.repo.SaveObject(ctx, objectKey, fileData, contentType); err != nil {
		return "", "", fmt.Errorf("failed to save object to repository: %w", err)
	}

	p := parser.GetParser(objectKey)
	parsedContent, err := p.Parse(fileData)
	if err != nil {
		return objectKey, fmt.Sprintf("File saved as %s, but parsing failed: %v", objectKey, err), nil
	}

	return objectKey, parsedContent, nil
}
