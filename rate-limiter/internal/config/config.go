package config

import (
	"errors"
	"os"

	"github.com/joho/godotenv"
)

type MedhubDB struct {
	DB_URL    string
	SecretKey string
}

func Load() (*MedhubDB, error) {
	_ = godotenv.Load(".env")
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
