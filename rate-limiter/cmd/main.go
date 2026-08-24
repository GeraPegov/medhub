package main

import (
	"net/http"
	"new_prog/internal/handler"
	"new_prog/internal/service"
	"new_prog/internal/storage/postgres"
)

func main() {
	postgres.StartPostgres()
	repository := postgres.NewRepository(postgres.Pool)
	adminService := service.NewAdminService(repository)
	adminHandler := handler.NewAdminHandler(adminService)

	// http.HandleFunc("/admin/info", handler.Info)
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
