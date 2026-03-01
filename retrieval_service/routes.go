package main

import (
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/nate/retrieval_service/handlers"
	"github.com/nate/retrieval_service/service"
)

func NewRouter(svc service.RetrievalService) *chi.Mux {
	r := chi.NewRouter()
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)

	// Initialize handlers
	evidenceHandler := handlers.NewEvidenceHandler(svc)

	// Define routes
	r.Get("/api/v1/evidence/{object_key}", evidenceHandler.GetEvidence)

	return r
}
