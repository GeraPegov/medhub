package storage

import (
	"context"
	"fmt"
	"time"

	"github.com/redis/go-redis/v9"
)

type RedisStorage struct {
	client *redis.Client
}

func NewRedisStorage(addr string, db int) (*RedisStorage, error) {
	client := redis.NewClient(&redis.Options{
		Addr: addr,
		DB:   db,
	})

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := client.Ping(ctx).Err(); err != nil {
		return nil, fmt.Errorf("failes to connect to Redis: %w", err)
	}

	return &RedisStorage{client: client}, nil
}

func (r *RedisStorage) IncrementCounter(ctx context.Context, key string, ttl time.Duration) (int64, error) {
	pipe := r.client.Pipeline()

	incrCmd := pipe.Incr(ctx, key)

	pipe.Expire(ctx, key, ttl)

	_, err := pipe.Exec(ctx)
	if err != nil {
		return 0, fmt.Errorf("failed to increment counter : %w", err)
	}

	return incrCmd.Val(), nil
}

func (r *RedisStorage) GetCounter(ctx context.Context, key string) (int64, error) {
	val, err := r.client.Get(ctx, key).Int64()
	if err == redis.Nil {
		return 0, nil
	}
	if err != nil {
		return 0, fmt.Errorf("failed to get counter: %w", err)
	}
	return val, nil
}

func (r *RedisStorage) Close() error {
	return r.client.Close()
}
