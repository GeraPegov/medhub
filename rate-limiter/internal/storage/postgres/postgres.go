package postgres

import (
	"context"
	"fmt"
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

func StartPostgres() {
	var err error
	Pool, err = pgxpool.New(context.Background(), config.MedhubDB)
	if err != nil {
		fmt.Println("не удалось подключится к постгрес")
	}

	if err := Pool.Ping(context.Background()); err != nil {
		fmt.Println("бд не отвечает")
	}

	fmt.Println("подключились к постгрес")
}
