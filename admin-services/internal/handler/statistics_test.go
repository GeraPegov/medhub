package handler

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"reflect"
	"testing"
	"time"

	"new_prog/internal/domain"
)

type statisticsHandlerStub struct {
	quantityUsers      int
	quantityArticles   int
	popularCategories  []domain.PopularCategory
	popularAuthors     []domain.PopularAuthors
	quantityUsersErr   error
	quantityArticleErr error
	popularCategoryErr error
	popularAuthorsErr  error
}

func (h *statisticsHandlerStub) QuantityUsers(context.Context, time.Time, time.Time) (int, error) {
	return h.quantityUsers, h.quantityUsersErr
}

func (h *statisticsHandlerStub) QuantityArticles(context.Context, time.Time, time.Time) (int, error) {
	return h.quantityArticles, h.quantityArticleErr
}

func (h *statisticsHandlerStub) PopularityCategory(context.Context, time.Time, time.Time) ([]domain.PopularCategory, error) {
	return h.popularCategories, h.popularCategoryErr
}

func (h *statisticsHandlerStub) PopularityAuthors(context.Context, time.Time, time.Time) ([]domain.PopularAuthors, error) {
	return h.popularAuthors, h.popularAuthorsErr
}

func TestStatistics(t *testing.T) {
	tests := []struct {
		name    string
		service *statisticsHandlerStub
		want    domain.StatisticsResponse
	}{
		{
			name: "returns statistics including a single list item",
			service: &statisticsHandlerStub{
				quantityUsers:    5,
				quantityArticles: 7,
				popularCategories: []domain.PopularCategory{
					{Category: "medicine", Quantity: 7},
				},
				popularAuthors: []domain.PopularAuthors{
					{Username: "doctor", UserId: 3, Quantity: 4},
				},
			},
			want: domain.StatisticsResponse{
				QuantityUsers:    domain.StatUsers{Value: 5},
				QuantityArticles: domain.StatArticles{Value: 7},
				PopularityCategory: domain.StatCategory{Value: []domain.PopularCategory{
					{Category: "medicine", Quantity: 7},
				}},
				PopularityAuthors: domain.StatAuthors{Value: []domain.PopularAuthors{
					{Username: "doctor", UserId: 3, Quantity: 4},
				}},
			},
		},
		{
			name:    "reports empty lists as no content",
			service: &statisticsHandlerStub{},
			want: domain.StatisticsResponse{
				QuantityUsers:      domain.StatUsers{},
				QuantityArticles:   domain.StatArticles{},
				PopularityCategory: domain.StatCategory{Err: statisticsNoContent},
				PopularityAuthors:  domain.StatAuthors{Err: statisticsNoContent},
			},
		},
		{
			name: "does not report service failures as no content",
			service: &statisticsHandlerStub{
				quantityUsersErr:   errors.New("quantity users failed"),
				quantityArticleErr: errors.New("quantity articles failed"),
				popularCategoryErr: errors.New("popular categories failed"),
				popularAuthorsErr:  errors.New("popular authors failed"),
			},
			want: domain.StatisticsResponse{
				QuantityUsers:      domain.StatUsers{Err: statisticsInternalError},
				QuantityArticles:   domain.StatArticles{Err: statisticsInternalError},
				PopularityCategory: domain.StatCategory{Err: statisticsInternalError},
				PopularityAuthors:  domain.StatAuthors{Err: statisticsInternalError},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			handler := NewStatisticsHandler(tt.service)
			request := httptest.NewRequest(
				http.MethodGet,
				"/admin/statistics?date_from=2026-01-01&date_to=2026-01-03",
				nil,
			)
			responseRecorder := httptest.NewRecorder()

			handler.Statistics(responseRecorder, request)

			if responseRecorder.Code != http.StatusOK {
				t.Fatalf("status code = %d, expected %d", responseRecorder.Code, http.StatusOK)
			}

			var got domain.StatisticsResponse
			if err := json.NewDecoder(responseRecorder.Body).Decode(&got); err != nil {
				t.Fatalf("decode response: %v", err)
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("response = %#v, expected %#v", got, tt.want)
			}
		})
	}
}
