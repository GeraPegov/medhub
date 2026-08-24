package postgres

import (
	"context"
	"fmt"
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
		return nil, err
	}
	defer rows.Close()

	comments := make([]domain.Comment, 0)
	for rows.Next() {
		var comment domain.Comment
		if err := rows.Scan(&comment.Id, &comment.Content, &comment.CreatedAt); err != nil {
			return nil, err
		}
		comments = append(comments, comment)
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return comments, nil
}

func (r *Repository) DeleteComment(ctx context.Context, id int) error {
	_, err := r.pool.Exec(ctx, "DELETE FROM comments WHERE id = $1", id)
	return err
}
