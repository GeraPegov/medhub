package config

import (
	"errors"
	"fmt"
	"os"

	"github.com/joho/godotenv"
)

type MedhubDB struct {
	DB_URL      string
	SecretKey   string
	TEST_DB_URL string
}

func Load() (*MedhubDB, error) {
	if err := godotenv.Load(".env"); err != nil && !errors.Is(err, os.ErrNotExist) {
		return nil, fmt.Errorf("load .env: %w", err)
	}
	db := MedhubDB{
		DB_URL:    os.Getenv("PROD_DB_URL"),
		SecretKey: os.Getenv("SECRET_KEY"),
	}
	if db.DB_URL == "" {
		return nil, errors.New("PROD_DB_URL is required")
	}
	if db.SecretKey == "" {
		return nil, errors.New("SECRET_KEY is required")
	}
	return &db, nil
}
