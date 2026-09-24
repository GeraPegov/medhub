package handler

// import (
// 	"net/http"
// 	"net/http/httptest"
// 	"testing"
// )

// func TestStatistics(t *testing.T) {
// 	service := &adminServiceStub{
// 		quantityUsers: 5,
// 		quantityArticles: 5,

// 	}
// 	handler := NewAdminHandler(service)

// 	r := httptest.NewRequest(
// 		http.MethodGet,
// 		"/admin/statistics",
// 		nil,
// 	)
// 	w := httptest.NewRecorder()

// 	handler.Statistics(w, r)
// }
