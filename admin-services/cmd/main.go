package main

import (
	"log/slog"
	"net/http"
	"new_prog/internal/config"
	"new_prog/internal/handler"
	"new_prog/internal/service"
	"new_prog/internal/storage/postgres"
	"os"
)

func main() {
	logger := slog.New(
		slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
			Level: slog.LevelInfo,
		}),
	)
	slog.SetDefault(logger)
	cfg, err := config.Load()
	if err != nil {
		panic(err)
	}
	service.GenerateKey(cfg)
	if err := postgres.StartPostgres(cfg); err != nil {
		slog.Error(
			"failed to start postgres",
			"operation", "StartPostgres",
			"error", err,
		)
		os.Exit(1)
	}
	defer postgres.Pool.Close()
	repository := postgres.NewRepository(postgres.Pool)
	adminService := service.NewAdminService(repository)
	adminHandler := handler.NewAdminHandler(adminService)

	http.HandleFunc("GET /admin/me", handler.AuthCheck)
	http.HandleFunc("POST /admin/register", handler.Register)
	http.HandleFunc("POST /admin/login", handler.Login)
	http.HandleFunc("GET /admin/users", adminHandler.GetUsers)
	http.HandleFunc("DELETE /admin/users/{id}", adminHandler.DeleteUser)
	http.HandleFunc("GET /admin/articles", adminHandler.GetArticles)
	http.HandleFunc("DELETE /admin/articles/{id}", adminHandler.DeleteArticle)
	http.HandleFunc("GET /admin/comments", adminHandler.GetComments)
	http.HandleFunc("DELETE /admin/comments/{id}", adminHandler.DeleteComment)
	http.HandleFunc("GET /admin/statistics", handler.Statistics)

	http.ListenAndServe(":8001", nil)
}
