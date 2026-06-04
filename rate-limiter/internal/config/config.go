package config

import (
	"new_prog/internal/domain"
)

var NewRedis domain.Redis = domain.Redis{
	Addr:     "localhost:6379",
	Password: "",
	DB:       0,
}
