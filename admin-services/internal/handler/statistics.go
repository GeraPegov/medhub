package handler

import (
	"context"
	"encoding/json"
	"net/http"
	"sync"
	"time"

	"new_prog/internal/domain"
)

type StatisticsService interface {
	QuantityUsers(context.Context, time.Time, time.Time) (int, error)
	QuantityArticles(context.Context, time.Time, time.Time) (int, error)
	PopularityCategory(context.Context, time.Time, time.Time) ([]domain.PopularCategory, error)
	PopularityAuthors(context.Context, time.Time, time.Time) ([]domain.PopularAuthors, error)
}

type StatisticsHandler struct {
	service StatisticsService
}

func NewStatisticsHandler(service StatisticsService) *StatisticsHandler {
	return &StatisticsHandler{service: service}
}

func (h *StatisticsHandler) Statistics(w http.ResponseWriter, r *http.Request) {
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
	popularityCategory := domain.StatCategory{}
	popularityAuthors := domain.StatAuthors{}

	var wg sync.WaitGroup

	wg.Add(4)

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

	go func() {
		defer wg.Done()
		q, err := h.service.PopularityCategory(ctx, dateFrom, dateTo)
		if err != nil {
			popularityCategory.Err = "no content"
			return
		}
		if len(q) == 1 || q[0].Err != "" {
			popularityCategory.Err = q[0].Err
			return
		}
		popularityCategory.Value = q
	}()

	go func() {
		defer wg.Done()
		q, err := h.service.PopularityAuthors(ctx, dateFrom, dateTo)
		if err != nil {
			popularityAuthors.Err = "no content"
			return
		}
		if len(q) == 1 || q[0].Err != "" {
			popularityAuthors.Err = q[0].Err
			return
		}
		popularityAuthors.Value = q
	}()

	wg.Wait()
	response := domain.StatisticsResponse{
		QuantityArticles:   quantityArticles,
		QuantityUsers:      quantityUsers,
		PopularityCategory: popularityCategory,
		PopularityAuthors:  popularityAuthors,
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(response); err != nil {
		return
	}
}
