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
	pipe := r.rdb.TxPipeline()
	key := fmt.Sprintf("%s:%s", userId, date)
	count := pipe.Incr(ctx, key)
	pipe.Expire(ctx, key, 24*time.Hour)
	if _, err := pipe.Exec(ctx); err != nil {
		slog.ErrorContext(ctx,
			"Failed to create increment",
			"Operation", "LimiterArticle",
			"error", err)
		return 0, domain.ErrRedis
	}
	return count.Val(), nil
}

func (r *Repository) LimiterComment(ctx context.Context, userId string, articleId string) (int64, error) {
	date := time.Now().Format("2006-01-02-15")
	key := fmt.Sprintf("user%s:article%s:%s", userId, articleId, date)
	pipe := r.rdb.TxPipeline()
	count := pipe.Incr(ctx, key)
	pipe.Expire(ctx, key, 24*time.Hour)
	if _, err := pipe.Exec(ctx); err != nil {
		slog.ErrorContext(ctx,
			"Failed to create increment",
			"Operation", "LimiterComment",
			"error", err)
		return 0, domain.ErrRedis
	}
	return count.Val(), nil
}
