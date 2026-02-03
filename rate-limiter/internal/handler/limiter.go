package handler

import (
	"net/http"

	"github.com/GeraPegov/rate-limiter/internal/service"
	"github.com/gin-gonic/gin"
)

type LimiterHandler struct {
	service *service.LimiterService
}

func NewLimiterHandler(service *service.LimiterService) *LimiterHandler {
	return &LimiterHandler{service: service}
}

// CheckLimit обрабатывает POST /check-limit
func (h *LimiterHandler) CheckLimit(c *gin.Context) {
	var req service.CheckLimitRequest

	// Парсим JSON из тела запроса
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Вызываем бизнес-логику
	resp, err := h.service.CheckAndIncrement(c.Request.Context(), req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	// Если лимит превышен → возвращаем 429
	if !resp.Allowed {
		c.Header("Retry-After", string(resp.RetryAfter))
		c.JSON(http.StatusTooManyRequests, resp)
		return
	}

	// Всё OK → 200
	c.JSON(http.StatusOK, resp)
}

// HealthCheck для мониторинга (GET /health)
func (h *LimiterHandler) HealthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}
