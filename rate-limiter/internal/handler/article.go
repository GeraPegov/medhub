package handler

import (
	"encoding/json"
	"fmt"
	"net/http"
	"new_prog/internal/storage/postgres"
	"time"
)

func GetArticles(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	articles, err := postgres.GetArticles(ctx)
	if err != nil {
		fmt.Println("Плохие новости при выдаче всех статей")
		return
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(articles)
}

func DeleteArticles(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	article_id := r.PathValue("id")
	err := postgres.DeleteArticles(ctx, article_id)
	if err != nil {
		fmt.Println("плохие новости при удалении статьи")
	} else {
		fmt.Println("хорошие новости при удалении статьи")
	}
}

func ArticlesRegDate(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	date := r.URL.Query().Get("date")
	_, err := time.Parse("2006-01-02", date)
	if err != nil {
		http.Error(w, "неправильный формат даты", http.StatusBadRequest)
	}
	articles, err := postgres.ArticlesByDate(ctx, date)
	if err != nil {
		fmt.Println("плохие новости при показе новых статей за день")
		return
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(articles)
}
