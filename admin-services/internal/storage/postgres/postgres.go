package postgres

import (
	"context"
	"fmt"
	"log/slog"
	"new_prog/internal/config"

	"github.com/jackc/pgx/v5/pgxpool"
)

type Repository struct {
	pool *pgxpool.Pool
}

func StartPostgres(cfg *config.MedhubDB) (*Repository, error) {
	pool, err := pgxpool.New(context.Background(), cfg.DB_URL)
	if err != nil {
		return nil, fmt.Errorf("create postgres pool: %w", err)
	}

	if err := pool.Ping(context.Background()); err != nil {
		pool.Close()
		return nil, fmt.Errorf("ping postgres: %w", err)
	}

	slog.Info(
		"connected to postgres",
		"operation", "StartPostgres",
	)
	return &Repository{pool: pool}, nil
}

func PostgresClose(repository *Repository) {
	repository.pool.Close()
}
