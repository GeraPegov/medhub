package domain

type StatArticles struct {
	Value int
	Err   string
}

type StatUsers struct {
	Value int
	Err   string
}

type StatCategory struct {
	Value []PopularCategory
	Err   string
}

type StatAuthors struct {
	Value []PopularAuthors
	Err   string
}

type StatisticsResponse struct {
	QuantityArticles   StatArticles `json:"quantity_articles"`
	QuantityUsers      StatUsers    `json:"quantity_users"`
	PopularityCategory StatCategory `json:"popularity_category"`
	PopularityAuthors  StatAuthors  `json:"popularity_authors"`
}

type PopularCategory struct {
	Category string
	Quantity int
}

type PopularAuthors struct {
	Username string
	UserId   int
	Quantity int
}
