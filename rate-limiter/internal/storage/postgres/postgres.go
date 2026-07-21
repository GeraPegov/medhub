package postgres

import (
	"context"
	"fmt"
	"new_prog/internal/config"

	"github.com/jackc/pgx/v5/pgxpool"
)

var Pool *pgxpool.Pool

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
