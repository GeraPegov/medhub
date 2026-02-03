package config

import (
	"log"
	"os"
	"strconv"
)

type Config struct {
	ServerPort string
	RedisAddr  string
	RedisDB    int
}

func LoadConfig() *Config {
	redisDB, err := strconv.Atoi(getEnv("REDIS_DB", "0"))

	if err != nil {
		log.Fatalf("Invalid REDIS_DB: %v", err)
	}

	return &Config{
		ServerPort: getEnv("SERVER_PORT", "8080"),
		RedisAddr:  getEnv("REDIS_ADDR", "localhost:6379"),
		RedisDB:    redisDB,
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
