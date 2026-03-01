package main

import (
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/nate/intake_service/handlers"
	"github.com/nate/intake_service/service"
)

func NewRouter(svc service.IntakeService) *chi.Mux {
	r := chi.NewRouter()
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)

	// Initialize handlers
	intakeHandler := handlers.NewIntakeHandler(svc)

	// Define routes
	r.Get("/api/v1/evidence/{object_key}", intakeHandler.GetEvidence)
	r.Post("/api/v1/intake", intakeHandler.IntakeFile)

	return r
}
