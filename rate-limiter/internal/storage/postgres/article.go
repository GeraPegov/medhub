package postgres

import (
	"context"
	"fmt"
	"new_prog/internal/domain"
	"strings"
)

func QuantityArticles(ctx context.Context) (int, error) {
	var quantityArticles int
	err := Pool.QueryRow(ctx, "SELECT COUNT(id) FROM articles").Scan(&quantityArticles)
	if err != nil {
		return 0, domain.ErrDatabase
	}
	return quantityArticles, nil
}

func (r *Repository) SearchArticles(ctx context.Context, filter domain.ArticleFilter) ([]domain.Article, error) {
	query := "SELECT id, title, user_id, created_at FROM articles"
	conditions := make([]string, 0, 3)
	args := make([]any, 0, 3)

	if filter.ID != nil {
		args = append(args, *filter.ID)
		conditions = append(conditions, fmt.Sprintf("id = $%d", len(args)))
	}
	if filter.UserID != nil {
		args = append(args, *filter.UserID)
		conditions = append(conditions, fmt.Sprintf("user_id = $%d", len(args)))
	}
	if filter.Title != "" {
		args = append(args, "%"+filter.Title+"%")
		conditions = append(conditions, fmt.Sprintf("title ILIKE $%d", len(args)))
	}
	if len(conditions) > 0 {
		query += " WHERE " + strings.Join(conditions, " AND ")
	}
	rows, err := r.pool.Query(ctx, query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	articles := make([]domain.Article, 0)
	for rows.Next() {
		var article domain.Article
		if err := rows.Scan(&article.Id, &article.Title, &article.UserID, &article.CreatedAt); err != nil {
			return nil, err
		}
		articles = append(articles, article)
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return articles, nil
}

func (r *Repository) DeleteArticle(ctx context.Context, id int) error {
	_, err := r.pool.Exec(ctx, "DELETE FROM articles WHERE id = $1", id)
	return err
}

func ArticlesByDate(ctx context.Context, date string) ([]domain.Article, error) {
	rows, err := Pool.Query(
		ctx,
		"SELECT id, title, user_id, created_at FROM articles WHERE created_at::date = $1",
		date,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	articles := make([]domain.Article, 0)
	for rows.Next() {
		var article domain.Article
		if err := rows.Scan(&article.Id, &article.Title, &article.UserID, &article.CreatedAt); err != nil {
			return nil, err
		}
		articles = append(articles, article)
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return articles, nil
}
