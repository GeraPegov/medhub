package main

import (
	"net/http"
	"new_prog/internal/handler"
	"new_prog/internal/storage/postgres"
)

func main() {
	postgres.StartPostgres()
	http.HandleFunc("/admin/info", handler.Info)
	http.HandleFunc("/admin/register", handler.Register)
	http.HandleFunc("/admin/login", handler.Login)
	http.HandleFunc("/admin/users", handler.SearchUsers)
	http.HandleFunc("/admin/users/delete", handler.UserDelete)
	http.HandleFunc("/admin/articles", handler.GetArticles)
	http.HandleFunc("/admin/articles/{id}", handler.DeleteArticles)
	http.HandleFunc("/admin/comments", handler.CommentsByArticle)
	http.HandleFunc("/admin/comments/delete", handler.CommentsDelete)

	http.ListenAndServe(":8001", nil)
}
