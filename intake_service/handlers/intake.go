package handlers

import (
	"encoding/json"
	"io"
	"log"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/nate/intake_service/service"
)

type IntakeHandler struct {
	svc service.IntakeService
}

func NewIntakeHandler(svc service.IntakeService) *IntakeHandler {
	return &IntakeHandler{svc: svc}
}

type GetEvidenceResponse struct {
	ObjectKey    string `json:"object_key"`
	Processed    bool   `json:"processed"`
	LLMReadyText string `json:"llm_ready_text"`
}

type IntakeResponse struct {
	ObjectKey     string `json:"object_key"`
	ExtractedText string `json:"extracted_text"`
}

func (h *IntakeHandler) GetEvidence(w http.ResponseWriter, r *http.Request) {
	objectKey := chi.URLParam(r, "object_key")
	if objectKey == "" {
		http.Error(w, "Object key is required", http.StatusBadRequest)
		return
	}

	processedText, err := h.svc.GetEvidence(objectKey)
	if err != nil {
		log.Printf("ERROR: %v", err)
		http.Error(w, "Failed to retrieve evidence", http.StatusInternalServerError)
		return
	}

	response := GetEvidenceResponse{
		ObjectKey:    objectKey,
		Processed:    true,
		LLMReadyText: processedText,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func (h *IntakeHandler) IntakeFile(w http.ResponseWriter, r *http.Request) {
	// 1. Parse the multipart form
	if err := r.ParseMultipartForm(10 << 20); err != nil { // 10 MB
		http.Error(w, "Failed to parse multipart form", http.StatusBadRequest)
		return
	}

	// 2. Get the file from the form
	file, handler, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Failed to retrieve file from form", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// 3. Read the file data
	fileBytes, err := io.ReadAll(file)
	if err != nil {
		http.Error(w, "Failed to read file data", http.StatusInternalServerError)
		return
	}

	// 4. Call the service layer to process and save the file
	objectKey, extractedText, err := h.svc.ProcessIntake(handler.Filename, fileBytes, handler.Header.Get("Content-Type"))
	if err != nil {
		log.Printf("ERROR: %v", err)
		http.Error(w, "Failed to process intake", http.StatusInternalServerError)
		return
	}

	// 5. Format and send the response
	response := IntakeResponse{
		ObjectKey:     objectKey,
		ExtractedText: extractedText,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(response)
}
