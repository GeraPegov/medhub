package handler

import (
	"context"
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

const (
	statisticsNoContent     = "no content"
	statisticsInternalError = "internal server error"
)

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
		quantity, err := h.service.QuantityUsers(ctx, dateFrom, dateTo)
		if err != nil {
			quantityUsers.Err = statisticsInternalError
			return
		}
		quantityUsers.Value = quantity
	}()

	go func() {
		defer wg.Done()
		quantity, err := h.service.QuantityArticles(ctx, dateFrom, dateTo)
		if err != nil {
			quantityArticles.Err = statisticsInternalError
			return
		}
		quantityArticles.Value = quantity
	}()

	go func() {
		defer wg.Done()
		categories, err := h.service.PopularityCategory(ctx, dateFrom, dateTo)
		if err != nil {
			popularityCategory.Err = statisticsInternalError
			return
		}
		if len(categories) == 0 {
			popularityCategory.Err = statisticsNoContent
			return
		}
		popularityCategory.Value = categories
	}()

	go func() {
		defer wg.Done()
		authors, err := h.service.PopularityAuthors(ctx, dateFrom, dateTo)
		if err != nil {
			popularityAuthors.Err = statisticsInternalError
			return
		}
		if len(authors) == 0 {
			popularityAuthors.Err = statisticsNoContent
			return
		}
		popularityAuthors.Value = authors
	}()

	wg.Wait()
	response := domain.StatisticsResponse{
		QuantityArticles:   quantityArticles,
		QuantityUsers:      quantityUsers,
		PopularityCategory: popularityCategory,
		PopularityAuthors:  popularityAuthors,
	}
	writeJSON(w, http.StatusOK, response)
}
