package domain

type TodayResponse struct {
	ArticlesToday    []Article    `json:"articles_today"`
	UsersToday       []User       `json:"users_today"`
	QuantityArticles StatArticles `json:"quantity_articles"`
	QuantityUsers    StatUsers    `json:"quantity_users"`
}
