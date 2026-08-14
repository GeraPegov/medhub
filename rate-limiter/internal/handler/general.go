package handler

import (
	"encoding/json"
	"fmt"
	"net/http"
	"new_prog/internal/domain"
	"new_prog/internal/storage/postgres"
	"time"

	"golang.org/x/sync/errgroup"
)

func Today(w http.ResponseWriter, r *http.Request) {
	date, err := time.Parse("2006-01-02", r.URL.Query().Get("date"))
	if err != nil {
		http.Error(w, "неправильный формат даты", http.StatusBadRequest)
		return
	}
	group, ctx := errgroup.WithContext(r.Context())
	var users []domain.User
	var articles []domain.Article
	group.Go(func() error {
		var err error
		articles, err = postgres.ArticlesByDate(ctx, date)
		if err != nil {
			return fmt.Errorf("get articles by date: %w", err)
		}
		return nil
	})

	group.Go(func() error {
		var err error
		users, err = postgres.UsersByDate(ctx, date)
		if err != nil {
			return fmt.Errorf("get users by date: %w", err)
		}
		return nil
	})

	if err := group.Wait(); err != nil {
		http.Error(w, "ошибка получения данных", http.StatusInternalServerError)
		return
	}
	type todayResponse struct {
		Articles []domain.Article `json:"articles"`
		Users    []domain.User    `json:"users"`
	}
	response := todayResponse{
		Articles: articles,
		Users:    users,
	}
	data, err := json.Marshal(response)
	if err != nil {
		http.Error(w, "ошибка сериализации", http.StatusInternalServerError)
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if _, err := w.Write(data); err != nil {
		return
	}

}
