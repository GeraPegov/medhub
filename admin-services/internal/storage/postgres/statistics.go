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
	rows, err := r.pool.Query(ctx, `
		SELECT category, COUNT(id)
		FROM articles
		WHERE created_at >= $1 AND created_at < $2
		GROUP BY category
		ORDER BY COUNT(id) DESC
		LIMIT 3
	`, dateFrom, dateTo)
	if err != nil {
		slog.ErrorContext(
			ctx,
			"failed to query popular categories",
			"operation", "PopularityCategory",
			"error", err,
		)
		return nil, domain.ErrDatabase
	}
	defer rows.Close()

	popularCategories := make([]domain.PopularCategory, 0)
	for rows.Next() {
		var popularCategory domain.PopularCategory

		if err := rows.Scan(&popularCategory.Category, &popularCategory.Quantity); err != nil {
			slog.ErrorContext(
				ctx,
				"failed to scan popular category",
				"operation", "PopularityCategory",
				"error", err,
			)
			return nil, domain.ErrDatabase
		}
		popularCategories = append(popularCategories, popularCategory)
	}
	if err := rows.Err(); err != nil {
		slog.ErrorContext(
			ctx,
			"failed while reading popular categories",
			"operation", "PopularityCategory",
			"error", err,
		)
		return nil, domain.ErrDatabase
	}

	return popularCategories, nil
}

func (r *Repository) PopularityAuthors(ctx context.Context, dateFrom time.Time, dateTo time.Time) ([]domain.PopularAuthors, error) {
	rows, err := r.pool.Query(ctx, `
		SELECT COUNT(articles.id), user_id, users.unique_username
		FROM articles
		JOIN users ON articles.user_id = users.id
		WHERE articles.created_at >= $1 AND articles.created_at < $2
		GROUP BY articles.user_id, users.unique_username
		ORDER BY COUNT(articles.id) DESC
		LIMIT 3
	`, dateFrom, dateTo)
	if err != nil {
		slog.ErrorContext(
			ctx,
			"failed to query popular authors",
			"operation", "PopularityAuthors",
			"error", err,
		)
		return nil, domain.ErrDatabase
	}
	defer rows.Close()

	popularAuthorsList := make([]domain.PopularAuthors, 0)
	for rows.Next() {
		var popularAuthors domain.PopularAuthors
		if err := rows.Scan(&popularAuthors.Quantity, &popularAuthors.UserId, &popularAuthors.Username); err != nil {
			slog.ErrorContext(
				ctx,
				"failed to scan popular author",
				"operation", "PopularityAuthors",
				"error", err,
			)
			return nil, domain.ErrDatabase
		}
		popularAuthorsList = append(popularAuthorsList, popularAuthors)
	}
	if err := rows.Err(); err != nil {
		slog.ErrorContext(
			ctx,
			"failed while reading popular authors",
			"operation", "PopularityAuthors",
			"error", err,
		)
		return nil, domain.ErrDatabase
	}

	return popularAuthorsList, nil
}
