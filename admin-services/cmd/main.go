package main

import (
	"errors"
	"log/slog"
	"net/http"
	"new_prog/internal/config"
	"new_prog/internal/handler"
	"new_prog/internal/service"
	"new_prog/internal/storage/postgres"
	"os"
)

func main() {
	mux := http.NewServeMux()
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

	mux.HandleFunc("POST /admin/register", handler.Register)
	mux.HandleFunc("POST /admin/login", handler.Login)
	mux.Handle("GET /admin/users", handler.RequireAdmin(http.HandlerFunc(adminHandler.GetUsers)))
	mux.Handle("DELETE /admin/users/{id}", handler.RequireAdmin(http.HandlerFunc(adminHandler.DeleteUser)))
	mux.Handle("GET /admin/articles", handler.RequireAdmin(http.HandlerFunc(adminHandler.GetArticles)))
	mux.Handle("DELETE /admin/articles/{id}", handler.RequireAdmin(http.HandlerFunc(adminHandler.DeleteArticle)))
	mux.Handle("GET /admin/comments", handler.RequireAdmin(http.HandlerFunc(adminHandler.GetComments)))
	mux.Handle("DELETE /admin/comments/{id}", handler.RequireAdmin(http.HandlerFunc(adminHandler.DeleteComment)))
	mux.Handle("GET /admin/statistics", handler.RequireAdmin(http.HandlerFunc(handler.Statistics)))

	address := ":8001"
	slog.Info("admin service started", "address", address)
	if err := http.ListenAndServe(address, mux); err != nil && !errors.Is(err, http.ErrServerClosed) {
		slog.Error("admin service stopped unexpectedly", "address", address, "error", err)
		os.Exit(1)
	}
}
