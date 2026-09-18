package redis

import (
	"context"
	"fmt"
	"log/slog"
	"new_prog/internal/domain"
	"time"
)

func (r *Repository) LimiterArticle(ctx context.Context, userId string) (int64, error) {
	date := time.Now().Format("2006-01-02")
	key := fmt.Sprintf("%s:%s", userId, date)
	num, err := r.rdb.Incr(ctx, key).Result()
	if err != nil {
		slog.ErrorContext(ctx,
			"Failed to create increment",
			"Operation", "LimiterArticle",
			"error", err)
		return 0, domain.ErrRedis
	}
	return num, nil
}

func (r *Repository) LimiterComment(ctx context.Context, userId string, articleId string) (int64, error) {
	date := time.Now().Format("2006-01-02-15")
	key := fmt.Sprintf("user%s:article%s:%s", userId, articleId, date)
	num, err := r.rdb.Incr(ctx, key).Result()
	if err != nil {
		slog.ErrorContext(ctx,
			"Failed to create increment",
			"Operation", "LimiterComment",
			"error", err)
		return 0, domain.ErrRedis
	}
	return num, nil
}
