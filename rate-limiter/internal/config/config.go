package config

import (
	"os"

	"github.com/joho/godotenv"
)

type MedhubDB struct {
	DB_URL    string
	SecretKey string
}

func Load() (*MedhubDB, error) {
	err := godotenv.Load(".env")
	if err != nil {
		return nil, err
	}
	db := MedhubDB{
		DB_URL:    os.Getenv("PROD_DB_URL"),
		SecretKey: os.Getenv("SECRET_KEY"),
	}
	return &db, nil
}
