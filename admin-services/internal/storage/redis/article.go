package redis

import (
	"context"
	"log/slog"
	"new_prog/internal/domain"
)

func (r *Repository) LimiterArticle(ctx context.Context, userId string) (int64, error) {
	num, err := r.rdb.Incr(ctx, userId).Result()
	if err != nil {
		slog.ErrorContext(ctx,
			"Failed to create increment",
			"Operation", "LimiterArticle",
			"error", err)
		return 0, domain.ErrRedis
	}
	return num, nil
}
