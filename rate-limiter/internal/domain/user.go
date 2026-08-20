package domain

import "time"

type User struct {
	Id               int       `json:"id"`
	Email            string    `json:"email"`
	UniqueUsername   string    `json:"username"`
	RegistrationDate time.Time `json:"registration_date"`
}

type StatUsers struct {
	Value int
	Err   string
}
