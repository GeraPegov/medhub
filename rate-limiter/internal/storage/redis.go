package storage

import (
	"context"
	"fmt"
	"log"
	"new_prog/internal/config"
	"sync"
	"time"

	"github.com/redis/go-redis/v9"
)

var rdb *redis.Client
var mu sync.Mutex

func CreateRedis() {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	rdb = redis.NewClient(&redis.Options{
		Addr:     config.NewRedis.Addr,
		Password: config.NewRedis.Password,
		DB:       config.NewRedis.DB,
	})

	pong, err := rdb.Ping(ctx).Result()
	if err != nil {
		log.Fatal("woow")
	}
	fmt.Println(pong)
}
