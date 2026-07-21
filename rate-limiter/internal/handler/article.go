package handler

import (
	"encoding/json"
	"fmt"
	"net/http"
	"new_prog/internal/storage/postgres"
	"time"
)

func AllArticles(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	articles, err := postgres.AllArticles(ctx)
	if err != nil {
		fmt.Println("Плохие новости при выдаче всех статей")
		return
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(articles)
}

func ArticleDelete(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	article_id := r.URL.Query().Get("id")
	err := postgres.ArticleDelete(ctx, article_id)
	if err != nil {
		fmt.Println("плохие новости при удалении статьи")
	} else {
		fmt.Println("хорошие новости при удалении статьи")
	}
}

func ArticlesToday(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	date, err := time.Parse("2006-01-02", r.URL.Query().Get("date"))
	if err != nil {
		http.Error(w, "неправильный формат даты", http.StatusBadRequest)
	}
	articles, err := postgres.GetArticlesByDate(ctx, date)
	if err != nil {
		fmt.Println("плохие новости при показе новых статей за день")
		return
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(articles)
}
