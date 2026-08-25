package postgres

import (
	"context"
	"fmt"
	"log/slog"
	"new_prog/internal/domain"
	"strings"
)

func (r *Repository) SearchComments(ctx context.Context, filter domain.CommentFilter) ([]domain.Comment, error) {
	query := "SELECT id, content, created_at FROM comments"
	conditions := make([]string, 0, 3)
	args := make([]any, 0, 3)

	if filter.ArticleID != nil {
		args = append(args, *filter.ArticleID)
		conditions = append(conditions, fmt.Sprintf("article_id = $%d", len(args)))
	}
	if filter.UserID != nil {
		args = append(args, *filter.UserID)
		conditions = append(conditions, fmt.Sprintf("user_id = $%d", len(args)))
	}
	if filter.Date != nil {
		args = append(args, filter.Date.Format("2006-01-02"))
		conditions = append(conditions, fmt.Sprintf("created_at::date = $%d", len(args)))
	}

	if len(conditions) > 0 {
		query += " WHERE " + strings.Join(conditions, " AND ")
	}

	rows, err := r.pool.Query(ctx, query, args...)
	if err != nil {
		slog.ErrorContext(
			ctx,
			"failed to search comments",
			"operation", "SearchComments",
			"article_id", filter.ArticleID,
			"user_id", filter.UserID,
			"date", filter.Date,
			"error", err,
		)
		return nil, domain.ErrDatabase
	}
	defer rows.Close()

	comments := make([]domain.Comment, 0)
	for rows.Next() {
		var comment domain.Comment
		if err := rows.Scan(&comment.Id, &comment.Content, &comment.CreatedAt); err != nil {
			slog.ErrorContext(
				ctx,
				"failed to scan comment",
				"operation", "SearchComments",
				"error", err,
			)
			return nil, domain.ErrDatabase
		}
		comments = append(comments, comment)
	}
	if err := rows.Err(); err != nil {
		slog.ErrorContext(
			ctx,
			"failed while iterating comments",
			"operation", "SearchComments",
			"error", err,
		)
		return nil, domain.ErrDatabase
	}
	return comments, nil
}

func (r *Repository) DeleteComment(ctx context.Context, id int) error {
	result, err := r.pool.Exec(ctx, "DELETE FROM comments WHERE id = $1", id)
	if err != nil {
		slog.ErrorContext(
			ctx,
			"failed to delete comment",
			"operation", "DeleteComment",
			"comment_id", id,
			"error", err,
		)
		return domain.ErrDatabase
	}
	if result.RowsAffected() == 0 {
		slog.WarnContext(
			ctx,
			"comment not found",
			"operation", "DeleteComment",
			"comment_id", id,
		)
		return domain.ErrRowsNotFound
	}
	return nil
}
