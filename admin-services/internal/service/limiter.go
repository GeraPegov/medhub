package service

import (
	"context"
	"log/slog"
)

type LimiterRepository interface {
	LimiterArticle(context.Context, string) (int64, error)
	LimiterComment(context.Context, string, string) (int64, error)
}

type LimiterService struct {
	repository LimiterRepository
}

func NewLimiterService(repository LimiterRepository) *LimiterService {
	return &LimiterService{repository: repository}
}

func (s *LimiterService) GetIncrementLimiterArticle(ctx context.Context, userId string) (int, error) {
	number, err := s.repository.LimiterArticle(ctx, userId)
	if err != nil {
		return 0, err
	}
	if number <= 3 {
		return 1, nil
	} else {
		slog.InfoContext(ctx, "Лимит на публикации статей", "Operation", "GetIncrementLimiterArticle", "userId", userId)
		return 0, nil
	}
}

func (s *LimiterService) GetIncrementLimiterComment(ctx context.Context, userId string, articleId string) (int, error) {
	number, err := s.repository.LimiterComment(ctx, userId, articleId)
	if err != nil {
		return 0, err
	}
	if number <= 10 {
		return 1, nil
	} else {
		slog.InfoContext(ctx, "Лимит на публикации комментариев", "Operation", "GetIncrementLimiterComment", "userId", userId, "articleId", articleId)
		return 0, nil
	}
}
