package service

import (
	"fmt"
	"github.com/google/uuid"
	"github.com/nate/intake_service/data"
	"github.com/nate/intake_service/service/parser"
	"path/filepath"
)

// IntakeService defines the business logic for processing and storing evidence.
type IntakeService interface {
	GetEvidence(objectKey string) (string, error)
	ProcessIntake(filename string, fileData []byte, contentType string) (string, string, error)
}

type intakeService struct {
	repo data.MinioRepository
}

// NewIntakeService creates a new instance of the intake service.
func NewIntakeService(repo data.MinioRepository) IntakeService {
	return &intakeService{repo: repo}
}

// GetEvidence fetches the object from the repository and parses it.
func (s *intakeService) GetEvidence(objectKey string) (string, error) {
	data, err := s.repo.GetObject(objectKey)
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
func (s *intakeService) ProcessIntake(filename string, fileData []byte, contentType string) (string, string, error) {
	// 1. Generate a unique key for the object
	ext := filepath.Ext(filename)
	objectKey := fmt.Sprintf("%s%s", uuid.New().String(), ext)

	// 2. Save the raw file to the repository
	if err := s.repo.SaveObject(objectKey, fileData, contentType); err != nil {
		return "", "", fmt.Errorf("failed to save object to repository: %w", err)
	}

	// 3. Select the correct parser and process the data
	p := parser.GetParser(objectKey)
	parsedContent, err := p.Parse(fileData)
	if err != nil {
		// Even if parsing fails, we've saved the file, so we don't treat this as a fatal error.
		return objectKey, fmt.Sprintf("File saved as %s, but parsing failed: %v", objectKey, err), nil
	}

	return objectKey, parsedContent, nil
}
