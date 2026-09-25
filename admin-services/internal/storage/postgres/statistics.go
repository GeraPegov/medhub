package postgres

import (
	"context"
	"log/slog"
	"new_prog/internal/domain"
	"time"
)

func (r *Repository) QuantityArticles(ctx context.Context, dateFrom time.Time, dateTo time.Time) (int, error) {
	var quantityArticles int
	err := r.pool.QueryRow(ctx, "SELECT COUNT(*) FROM articles WHERE created_at >= $1 and created_at < $2", dateFrom, dateTo).Scan(&quantityArticles)
	if err != nil {
		slog.ErrorContext(
			ctx,
			"failed to count articles",
			"operation", "QuantityArticles",
			"error", err,
		)
		return 0, domain.ErrDatabase
	}
	return quantityArticles, nil
}

func (r *Repository) QuantityUsers(ctx context.Context, dateFrom time.Time, dateTo time.Time) (int, error) {
	var quantityUsers int
	err := r.pool.QueryRow(ctx, "SELECT COUNT(*) FROM users WHERE registration_date >= $1 AND registration_date < $2", dateFrom, dateTo).Scan(&quantityUsers)
	if err != nil {
		slog.ErrorContext(
			ctx,
			"failed to count users",
			"operation", "QuantityUsers",
			"error", err,
		)
		return 0, domain.ErrDatabase
	}
	return quantityUsers, nil
}

func (r *Repository) PopularityCategory(ctx context.Context, dateFrom time.Time, dateTo time.Time) ([]domain.PopularCategory, error) {
	check_rows := false
	rows, err := r.pool.Query(ctx, `
		SELECT category, COUNT(id)
		FROM articles
		GROUP BY category
		ORDER BY COUNT(id) DESC
		LIMIT 3
	`)
	if err != nil {
		slog.ErrorContext(ctx,
			"Error database to request",
			"operation", "PopularityCategory",
			"err", err,
		)
		return nil, domain.ErrDatabase
	}
	listWithPopularCategory := []domain.PopularCategory{}
	for rows.Next() {
		check_rows = true
		var popularCategory domain.PopularCategory

		err := rows.Scan(&popularCategory.Category, &popularCategory.Quantity)
		if err != nil {
			slog.ErrorContext(ctx,
				"Failed for scan rows",
				"operation", "PopularityCategory",
				"err", err,
			)
			return nil, domain.ErrDatabase
		}
		listWithPopularCategory = append(listWithPopularCategory, popularCategory)
	}
	if check_rows == false {
		slog.Info("Nothing found popular category")
		listWithPopularCategory = append(listWithPopularCategory, domain.PopularCategory{Err: "not found popular category"})
		return listWithPopularCategory, nil
	}
	return listWithPopularCategory, nil
}

func (r *Repository) PopularityAuthors(ctx context.Context, dateFrom time.Time, dateTo time.Time) ([]domain.PopularAuthors, error) {
	check_rows := false
	rows, err := r.pool.Query(ctx, `
		SELECT COUNT(articles.id), user_id, users.unique_username
		FROM articles
		JOIN users ON articles.user_id = users.id
		GROUP BY articles.user_id, users.unique_username
		ORDER BY COUNT(articles.id) DESC
		LIMIT 3
	`)
	if err != nil {
		slog.ErrorContext(ctx,
			"Error database to request",
			"operation", "PopularityAuthors",
			"err", err,
		)
		return nil, domain.ErrDatabase
	}
	var listWithPopularAuthors []domain.PopularAuthors
	for rows.Next() {
		check_rows = true
		var popularAuthors domain.PopularAuthors
		err := rows.Scan(&popularAuthors.Quantity, &popularAuthors.UserId, &popularAuthors.Username)
		if err != nil {
			slog.ErrorContext(ctx,
				"Failed for scan rows",
				"operation", "PopularityCategory",
				"err", err,
			)
			return nil, domain.ErrDatabase
		}
		listWithPopularAuthors = append(listWithPopularAuthors, popularAuthors)
	}
	if check_rows == false {
		slog.Info("Nothing found popular authors")
		listWithPopularAuthors = append(listWithPopularAuthors, domain.PopularAuthors{Err: "not found popular authours"})
		return listWithPopularAuthors, nil
	}
	return listWithPopularAuthors, nil
}
