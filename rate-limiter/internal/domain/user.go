package domain

import "time"

type User struct {
	Id               int
	Email            string
	UniqueUsername   string
	RegistrationDate time.Time
}

type StatUsers struct {
	Value int
	Err   string
}
