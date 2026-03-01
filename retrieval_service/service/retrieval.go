package service

import (
	"fmt"
	"github.com/nate/retrieval_service/data"
	"github.com/nate/retrieval_service/service/parser"
)

// RetrievalService defines the business logic for retrieving and processing evidence.
type RetrievalService interface {
	GetEvidence(objectKey string) (string, error)
}

type retrievalService struct {
	repo data.MinioRepository
}

// NewRetrievalService creates a new instance of the retrieval service.
func NewRetrievalService(repo data.MinioRepository) RetrievalService {
	return &retrievalService{repo: repo}
}

// GetEvidence fetches the object from the repository and parses it using the appropriate parser.
func (s *retrievalService) GetEvidence(objectKey string) (string, error) {
	// 1. Fetch raw data from the repository
	data, err := s.repo.GetObject(objectKey)
	if err != nil {
		return "", fmt.Errorf("failed to retrieve object '%s': %w", objectKey, err)
	}

	// 2. Select the correct parser based on the file extension
	p := parser.GetParser(objectKey)

	// 3. Parse the data
	parsedContent, err := p.Parse(data)
	if err != nil {
		return "", fmt.Errorf("failed to parse object '%s': %w", objectKey, err)
	}

	return parsedContent, nil
}
