package redis

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/redis/go-redis/v9"
)

var rdb *redis.Client

func TestMain(m *testing.M) {
	rdb = redis.NewClient(&redis.Options{
		Addr:     "localhost:6379",
		Password: "",
		DB:       1,
		Protocol: 2,
	})

	m.Run()

}

func TestLimiterArticle(t *testing.T) {
	repository := &Repository{rdb: rdb}
	userId := "1"
	t.Cleanup(func() {
		date := time.Now().Format("2006-01-02")
		key := fmt.Sprintf("%s:%s", userId, date)
		err := repository.rdb.Del(context.Background(), key).Err()
		if err != nil {
			t.Errorf("delete Redis test key %q: %v", key, err)
		}
	})
	num, err := repository.LimiterArticle(context.Background(), userId)
	if num != 1 {
		t.Fatalf("LimiterArticle() returned %d, excpected 1", num)
	}
	if err != nil {
		t.Fatalf("LimiterArticle() excepcted error, %e", err)
	}

	num, err = repository.LimiterArticle(context.Background(), userId)
	if num != 2 {
		t.Fatalf("LimiterArticle() returned %d, excpected 2", num)
	}
	if err != nil {
		t.Fatalf("LimiterArticle() excepcted error, %e", err)
	}
}

func TestLimiterComment(t *testing.T) {
	repository := &Repository{rdb: rdb}
	userId := "1"
	articleId := "1"

	t.Cleanup(func() {
		date := time.Now().Format("2006-01-02-15")
		key := fmt.Sprintf("user%s:article%s:%s", userId, articleId, date)
		err := repository.rdb.Del(context.Background(), key).Err()
		if err != nil {
			t.Errorf("delete Redis test key %q: %v", key, err)
		}
	})
	num, err := repository.LimiterComment(context.Background(), userId, articleId)
	if num != 1 {
		t.Fatalf("LimiterComment() returned %d, excpected 1", num)
	}
	if err != nil {
		t.Fatalf("LimiterComment() excepcted error, %e", err)
	}

	num, err = repository.LimiterComment(context.Background(), userId, articleId)
	if num != 2 {
		t.Fatalf("LimiterComment() returned %d, excpected 2", num)
	}
	if err != nil {
		t.Fatalf("LimiterComment() excepcted error, %e", err)
	}
}
