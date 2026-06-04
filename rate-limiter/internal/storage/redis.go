package storage

import (
	"context"
	"fmt"
	"log"
	"new_prog/internal/config"
	"new_prog/internal/domain"
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

func Save(ctx context.Context, user domain.User) {
	mu.Lock()
	defer mu.Unlock()
	now_time := time.Now().Format("03:04")
	count, err := rdb.Get(ctx, now_time).Int()
	if err != nil && err != redis.Nil {
		fmt.Println(err)
		return
	}
	if count > 5 {
		fmt.Println("dohuya")
		return
	}
	rdb.Incr(ctx, now_time)
	user_id, _ := rdb.Incr(ctx, "id").Result()
	key := fmt.Sprintf("user:%d", user_id)
	err = rdb.Set(ctx, key, user.Name, 10*time.Minute).Err()
	if err != nil {
		fmt.Println("warning in Set ")
	}
}

func Get(ctx context.Context, id string) string {
	from := fmt.Sprintf("user:%s", id)
	msg, err := rdb.Get(ctx, from).Result()
	if err != nil {
		fmt.Println("not in redis")
	}
	return msg
}
