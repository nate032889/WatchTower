package handlers

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/nate/retrieval_service/service"
)

type EvidenceHandler struct {
	svc service.RetrievalService
}

func NewEvidenceHandler(svc service.RetrievalService) *EvidenceHandler {
	return &EvidenceHandler{svc: svc}
}

type EvidenceResponse struct {
	ObjectKey    string `json:"object_key"`
	Processed    bool   `json:"processed"`
	LLMReadyText string `json:"llm_ready_text"`
}

func (h *EvidenceHandler) GetEvidence(w http.ResponseWriter, r *http.Request) {
	objectKey := chi.URLParam(r, "object_key")
	if objectKey == "" {
		http.Error(w, "Object key is required", http.StatusBadRequest)
		return
	}

	// Call the service layer
	processedText, err := h.svc.GetEvidence(objectKey)
	if err != nil {
		log.Printf("ERROR: %v", err)
		http.Error(w, "Failed to retrieve evidence", http.StatusInternalServerError)
		return
	}

	// Format the response
	response := EvidenceResponse{
		ObjectKey:    objectKey,
		Processed:    true,
		LLMReadyText: processedText,
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(response); err != nil {
		log.Printf("ERROR: Failed to encode JSON response: %v", err)
	}
}
