package handler

import (
	"encoding/json"
	"fmt"
	"net/http"
	"new_prog/internal/storage/postgres"
)

func CommentsByArticle(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	articleId := r.URL.Query().Get("id")
	comments, err := postgres.CommentsByArticle(ctx, articleId)
	if err != nil {
		fmt.Println("Плохие новости в комментариях ")
	}
	json.NewEncoder(w).Encode(comments)
}

func CommentsDelete(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	commentId := r.URL.Query().Get("id")
	err := postgres.CommentsDelete(ctx, commentId)
	if err != nil {
		fmt.Println("плохие новости при удалении коментария")
	}
}
