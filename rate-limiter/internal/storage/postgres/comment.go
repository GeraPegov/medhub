package postgres

import (
	"context"
	"new_prog/internal/domain"
)

func CommentsByArticle(ctx context.Context, article_id string) ([]domain.Comment, error) {
	rows, err := Pool.Query(ctx, "SELECT id, content, created_at FROM comments WHERE article_id = $1", article_id)
	if err != nil {
		return nil, err
	}
	var Comments []domain.Comment
	for rows.Next() {
		var c domain.Comment
		rows.Scan(&c.Id, &c.Content, &c.Created_at)
		Comments = append(Comments, c)
	}
	return Comments, nil
}

func CommentsDelete(ctx context.Context, comments_id string) error {
	_, err := Pool.Exec(ctx, "DELETE FROM comments WHERE id = $1", comments_id)
	return err
}
