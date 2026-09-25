package service

import (
	"context"
	"new_prog/internal/domain"
	"time"
)

type StatisticsRepository interface {
	QuantityUsers(context.Context, time.Time, time.Time) (int, error)
	QuantityArticles(context.Context, time.Time, time.Time) (int, error)
	PopularityCategory(context.Context, time.Time, time.Time) ([]domain.PopularCategory, error)
	PopularityAuthors(context.Context, time.Time, time.Time) ([]domain.PopularAuthors, error)
}

type StatisticsService struct {
	repository StatisticsRepository
}

func NewStatisticsService(repository StatisticsRepository) *StatisticsService {
	return &StatisticsService{repository: repository}
}

func (s *StatisticsService) QuantityUsers(ctx context.Context, dateFrom time.Time, dateTo time.Time) (int, error) {
	return s.repository.QuantityUsers(ctx, dateFrom, dateTo)
}

func (s *StatisticsService) QuantityArticles(ctx context.Context, dateFrom time.Time, dateTo time.Time) (int, error) {
	return s.repository.QuantityArticles(ctx, dateFrom, dateTo)
}

func (s *StatisticsService) PopularityCategory(ctx context.Context, dateFrom time.Time, dateTo time.Time) ([]domain.PopularCategory, error) {
	return s.repository.PopularityCategory(ctx, dateFrom, dateTo)
}

func (s *StatisticsService) PopularityAuthors(ctx context.Context, dateFrom time.Time, dateTo time.Time) ([]domain.PopularAuthors, error) {
	return s.repository.PopularityAuthors(ctx, dateFrom, dateTo)
}
