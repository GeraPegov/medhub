package domain

type TodayResponse struct {
	QuantityArticles StatArticles `json:"quantity_articles"`
	QuantityUsers    StatUsers    `json:"quantity_users"`
}
