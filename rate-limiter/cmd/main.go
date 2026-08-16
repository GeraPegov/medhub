package main

import (
	"net/http"
	"new_prog/internal/handler"
	"new_prog/internal/storage/postgres"
)

func main() {
	postgres.StartPostgres()
	// http.HandleFunc("/admin/info", handler.Info)
	http.HandleFunc("/admin/me", handler.AuthCheck)
	http.HandleFunc("/admin/register", handler.Register)
	http.HandleFunc("/admin/login", handler.Login)
	http.HandleFunc("/admin/users", handler.SearchUsers)
	http.HandleFunc("/admin/users/{id}", handler.UserDelete)
	http.HandleFunc("/admin/articles", handler.GetArticles)
	http.HandleFunc("/admin/articles/{id}", handler.DeleteArticles)
	http.HandleFunc("/admin/comments", handler.CommentsByArticle)
	http.HandleFunc("/admin/comments/{id}", handler.CommentsDelete)
	http.HandleFunc("/admin/statistics", handler.Statistics)

	http.ListenAndServe(":8001", nil)
}
