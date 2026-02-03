package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/GeraPegov/rate-limiter/internal/config"
	"github.com/GeraPegov/rate-limiter/internal/handler"
	"github.com/GeraPegov/rate-limiter/internal/service"
	"github.com/GeraPegov/rate-limiter/internal/storage"
	"github.com/gin-gonic/gin"
)

func main() {
	// 1. Загружаем конфигурацию
	cfg := config.LoadConfig()

	// 2. Подключаемся к Redis
	redisStorage, err := storage.NewRedisStorage(cfg.RedisAddr, cfg.RedisDB)
	if err != nil {
		log.Fatalf("Failed to connect to Redis: %v", err)
	}
	defer redisStorage.Close()

	// 3. Создаём сервис и handler
	limiterService := service.NewLimiterService(redisStorage)
	limiterHandler := handler.NewLimiterHandler(limiterService)

	// 4. Настраиваем HTTP роутер
	router := gin.Default()

	router.GET("/health", limiterHandler.HealthCheck)
	router.POST("/check-limit", limiterHandler.CheckLimit)

	// 5. Настраиваем HTTP сервер
	srv := &http.Server{
		Addr:    ":" + cfg.ServerPort,
		Handler: router,
	}

	// 6. Запускаем сервер в отдельной goroutine
	go func() {
		log.Printf("Starting server on port %s", cfg.ServerPort)
		err := srv.ListenAndServe()
		if err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server failed: %v", err)
		}
	}()

	// 7. Graceful shutdown при SIGINT/SIGTERM
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	log.Println("Server exited")
}
