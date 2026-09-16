package redis

import (
	"github.com/redis/go-redis/v9"
)

type Repository struct {
	rdb *redis.Client
}

func GetRedis() *Repository {
	rdb := redis.NewClient(&redis.Options{
		Addr:     "localhost:6379",
		Password: "",
		DB:       0,
		Protocol: 2,
	})

	return &Repository{rdb: rdb}
}

func RedisClose(rdb *Repository) {
	rdb.rdb.Close()
}
