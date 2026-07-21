package config

import (
	"new_prog/internal/domain"
)

var NewRedis domain.Redis = domain.Redis{
	Addr:     "localhost:6379",
	Password: "",
	DB:       0,
}

var MedhubDB string = "postgres://postgres:2710@localhost:5432/medhub"
