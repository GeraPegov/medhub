package postgres

import (
	"context"
	"new_prog/internal/domain"
	"time"
)

func GetArticles(ctx context.Context) ([]domain.Article, error) {
	rows, err := Pool.Query(ctx, "SELECT id, title, user_id, created_at from articles")
	if err != nil {
		return nil, err
	}
	var Articles []domain.Article
	for rows.Next() {
		var a domain.Article
		rows.Scan(&a.Id, &a.Title, &a.User_id, &a.Created_at)
		Articles = append(Articles, a)
	}
	return Articles, nil
}

func DeleteArticles(ctx context.Context, articleId string) error {
	_, err := Pool.Exec(ctx, "DELETE FROM articles WHERE id = $1", articleId)
	return err
}

func ArticlesByDate(ctx context.Context, date time.Time) ([]domain.Article, error) {

	rows, err := Pool.Query(ctx, "SELECT id, title, user_id, created_at FROM articles WHERE created_at::date = $1", date)

	if err != nil {
		return nil, err
	}
	var Articles []domain.Article
	for rows.Next() {
		var a domain.Article
		if err := rows.Scan(&a.Id, &a.Title, &a.User_id, &a.Created_at); err != nil {
			return nil, err
		}
		Articles = append(Articles, a)
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	defer rows.Close()
	return Articles, nil
}
