package service

import "context"

type LimiterRepository interface {
	LimiterArticle(context.Context, string) (int64, error)
}

type LimiterService struct {
	repository LimiterRepository
}

func NewLimiterService(repository LimiterRepository) *LimiterService {
	return &LimiterService{repository: repository}
}

func (s *LimiterService) GetIncrementLimiterArticle(ctx context.Context, userId string) (int64, error) {
	return s.repository.LimiterArticle(ctx, userId)
}
