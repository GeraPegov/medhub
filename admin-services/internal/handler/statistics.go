package handler

import (
	"encoding/json"
	"net/http"
	"new_prog/internal/domain"
	"new_prog/internal/storage/postgres"
	"sync"
)

func Statistics(w http.ResponseWriter, r *http.Request) {
	date := r.URL.Query().Get("date")
	ctx := r.Context()

	var usersToday []domain.User
	var articlesToday []domain.Article

	quantityUsers := domain.StatUsers{}
	quantityArticles := domain.StatArticles{}

	var wg sync.WaitGroup

	wg.Add(4)

	go func() {
		defer wg.Done()
		q, err := postgres.QuantityUsers(ctx)
		if err != nil {
			quantityUsers.Err = "no content"
			return
		}
		quantityUsers.Value = q
	}()

	go func() {
		defer wg.Done()
		q, err := postgres.QuantityArticles(ctx)
		if err != nil {
			quantityArticles.Err = "no content"
			return
		}
		quantityArticles.Value = q
	}()

	go func() {
		defer wg.Done()
		var err error
		articlesToday, err = postgres.ArticlesByDate(ctx, date)
		if err != nil {
			articlesToday = []domain.Article{}
		}
	}()

	go func() {
		defer wg.Done()
		var err error
		usersToday, err = postgres.UsersByDate(ctx, date)
		if err != nil {
			usersToday = []domain.User{}
		}
	}()
	wg.Wait()
	response := domain.TodayResponse{
		ArticlesToday:    articlesToday,
		UsersToday:       usersToday,
		QuantityArticles: quantityArticles,
		QuantityUsers:    quantityUsers,
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(response); err != nil {
		return
	}
}
