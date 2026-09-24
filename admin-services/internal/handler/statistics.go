package handler

import (
	"encoding/json"
	"net/http"
	"sync"
	"time"

	"new_prog/internal/domain"
)

func (h *AdminHandler) Statistics(w http.ResponseWriter, r *http.Request) {
	dateFrom, err := time.Parse("2006-01-02", r.URL.Query().Get("date_from"))
	if err != nil {
		responseError(w, http.StatusBadRequest, "failed parse the date from")
		return
	}
	dateTo, err := time.Parse("2006-01-02", r.URL.Query().Get("date_to"))
	if err != nil {
		responseError(w, http.StatusBadRequest, "failed parse the date to")
		return
	}
	ctx := r.Context()
	quantityUsers := domain.StatUsers{}
	quantityArticles := domain.StatArticles{}

	var wg sync.WaitGroup

	wg.Add(2)

	go func() {
		defer wg.Done()
		q, err := h.service.QuantityUsers(ctx, dateFrom, dateTo)
		if err != nil {
			quantityUsers.Err = "no content"
			return
		}
		quantityUsers.Value = q
	}()

	go func() {
		defer wg.Done()
		q, err := h.service.QuantityArticles(ctx, dateFrom, dateTo)
		if err != nil {
			quantityArticles.Err = "no content"
			return
		}
		quantityArticles.Value = q
	}()

	wg.Wait()
	response := domain.TodayResponse{
		QuantityArticles: quantityArticles,
		QuantityUsers:    quantityUsers,
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(response); err != nil {
		return
	}
}
