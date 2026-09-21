package config

import (
	"errors"
	"os"

	"github.com/joho/godotenv"
)

type MedhubDB struct {
	DB_URL      string
	SecretKey   string
	TEST_DB_URL string
}

func Load() (*MedhubDB, error) {
	_ = godotenv.Load(".env")
	db := MedhubDB{
		DB_URL:      os.Getenv("PROD_DB_URL"),
		SecretKey:   os.Getenv("SECRET_KEY"),
		TEST_DB_URL: os.Getenv("TEST_DB_URL"),
	}
	if db.DB_URL == "" {
		return nil, errors.New("PROD_DB_URL is required")
	}
	if db.SecretKey == "" {
		return nil, errors.New("SECRET_KEY is required")
	}
	if db.TEST_DB_URL == "" {
		return nil, errors.New("TEST_DB_URL is required")
	}
	return &db, nil
}
