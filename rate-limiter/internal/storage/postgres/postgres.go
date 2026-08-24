package postgres

import (
	"context"
	"fmt"
	"log/slog"
	"new_prog/internal/config"

	"github.com/jackc/pgx/v5/pgxpool"
)

var Pool *pgxpool.Pool

type Repository struct {
	pool *pgxpool.Pool
}

func NewRepository(pool *pgxpool.Pool) *Repository {
	return &Repository{pool: pool}
}

func StartPostgres(cfg *config.MedhubDB) error {
	pool, err := pgxpool.New(context.Background(), cfg.DB_URL)
	if err != nil {
		return fmt.Errorf("create postgres pool: %w", err)
	}

	if err := pool.Ping(context.Background()); err != nil {
		pool.Close()
		return fmt.Errorf("ping postgres: %w", err)
	}

	Pool = pool
	slog.Info(
		"connected to postgres",
		"operation", "StartPostgres",
	)
	return nil
}
