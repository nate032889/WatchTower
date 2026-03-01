package main

import (
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/nate032889/WatchTower/intake_service/handlers"
	"github.com/nate032889/WatchTower/intake_service/service"
)

func NewRouter(svc service.IntakeService) *chi.Mux {
	r := chi.NewRouter()
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)

	intakeHandler := handlers.NewIntakeHandler(svc)

	// All routes are now nested under the /v1 group
	r.Route("/v1", func(r chi.Router) {
		r.Get("/evidence/{object_key}", intakeHandler.GetEvidence)
		r.Post("/intake", intakeHandler.IntakeFile)
	})

	return r
}
