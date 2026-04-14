package main

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"log/slog"
	"math"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

// Service represents a public service from the municipal catalog.
type Service struct {
	ID           string   `json:"id"`
	Title        string   `json:"title"`
	Description  string   `json:"description"`
	Category     string   `json:"category"`
	Tags         []string `json:"tags"`
	Organization string   `json:"organization"`
	URL          string   `json:"url,omitempty"`
	ViewCount    int      `json:"view_count"`
	Active       bool     `json:"active"`
}

// PaginatedResponse wraps a paginated list of services.
type PaginatedResponse struct {
	Data       interface{} `json:"data"`
	Total      int         `json:"total"`
	Page       int         `json:"page"`
	PerPage    int         `json:"per_page"`
	TotalPages int         `json:"total_pages"`
}

// In-memory service store — 11 items.
var serviceStore = []Service{
	{
		ID: "s001", Title: "Cartão Rio",
		Description:  "Cartão de benefícios da Prefeitura do Rio de Janeiro para cidadãos em situação de vulnerabilidade social.",
		Category:     "beneficios",
		Tags:         []string{"cartao", "beneficio", "social"},
		Organization: "SMAS", ViewCount: 1523, Active: true,
	},
	{
		ID: "s002", Title: "Vacinação Gratuita",
		Description:  "Programa de vacinação gratuita nas Clínicas da Família em toda a cidade.",
		Category:     "saude",
		Tags:         []string{"vacina", "saude", "gratuito"},
		Organization: "SMS", ViewCount: 2301, Active: true,
	},
	{
		ID: "s003", Title: "Matrícula Escolar",
		Description:  "Processo de matrícula nas escolas municipais do Rio de Janeiro para o próximo ano letivo.",
		Category:     "educacao",
		Tags:         []string{"escola", "matricula", "educacao"},
		Organization: "SME", ViewCount: 4102, Active: true,
	},
	{
		ID: "s004", Title: "Regularização de Imóvel",
		Description:  "Serviço de regularização fundiária e emissão de documentos de propriedade para moradores.",
		Category:     "habitacao",
		Tags:         []string{"imovel", "documento", "regularizacao"},
		Organization: "SMPU", ViewCount: 876, Active: true,
	},
	{
		ID: "s005", Title: "Curso de Capacitação Profissional",
		Description:  "Cursos gratuitos de qualificação profissional para cidadãos cariocas em diversas áreas.",
		Category:     "trabalho",
		Tags:         []string{"curso", "capacitacao", "emprego", "qualificacao"},
		Organization: "SMTE", ViewCount: 3210, Active: true,
	},
	{
		ID: "s006", Title: "Passe Livre para Idosos",
		Description:  "Cartão de passe livre para cidadãos com 60 anos ou mais no transporte público municipal.",
		Category:     "transporte",
		Tags:         []string{"onibus", "idoso", "gratuito", "passe"},
		Organization: "SMTR", ViewCount: 1890, Active: true,
	},
	{
		ID: "s007", Title: "CRAS — Centro de Referência de Assistência Social",
		Description:  "Atendimento especializado para famílias em situação de vulnerabilidade social e risco pessoal.",
		Category:     "assistencia_social",
		Tags:         []string{"cras", "social", "familia", "vulnerabilidade"},
		Organization: "SMAS", ViewCount: 945, Active: true,
	},
	{
		ID: "s008", Title: "Coleta Seletiva",
		Description:  "Programa municipal de coleta seletiva de resíduos recicláveis com pontos em toda a cidade.",
		Category:     "meio_ambiente",
		Tags:         []string{"reciclagem", "lixo", "ambiental"},
		Organization: "COMLURB", ViewCount: 421, Active: true,
	},
	{
		ID: "s009", Title: "Alvará de Funcionamento",
		Description:  "Emissão e renovação de alvará para funcionamento de estabelecimentos comerciais e de serviços.",
		Category:     "empresas",
		Tags:         []string{"alvara", "comercio", "empresa", "licenca"},
		Organization: "SMF", ViewCount: 1234, Active: true,
	},
	{
		ID: "s010", Title: "Clínica da Família",
		Description:  "Atendimento de saúde primária e preventiva nas Clínicas da Família distribuídas pela cidade.",
		Category:     "saude",
		Tags:         []string{"clinica", "saude", "atendimento", "prevencao"},
		Organization: "SMS", ViewCount: 5678, Active: true,
	},
	{
		ID: "s011", Title: "Bolsa Família — Cadastramento",
		Description:  "Cadastramento e atualização no programa federal Bolsa Família nos postos municipais.",
		Category:     "beneficios",
		Tags:         []string{"bolsa", "beneficio", "renda", "federal"},
		Organization: "SMAS", ViewCount: 2987, Active: true,
	},
}

func findServiceByID(id string) *Service {
	for i := range serviceStore {
		if serviceStore[i].ID == id {
			return &serviceStore[i]
		}
	}
	return nil
}

func filterByQuery(query string) []Service {
	q := strings.ToLower(query)
	var results []Service
	for _, s := range serviceStore {
		if strings.Contains(strings.ToLower(s.Title), q) ||
			strings.Contains(strings.ToLower(s.Description), q) ||
			strings.Contains(strings.ToLower(s.Category), q) {
			results = append(results, s)
		}
	}
	return results
}

// authMiddleware validates the Authorization header.
// Valid token: "Bearer qa-challenge-token"
func authMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		auth := c.GetHeader("Authorization")
		if !strings.HasPrefix(auth, "Bearer ") {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "missing authorization header"})
			return
		}
		token := strings.TrimPrefix(auth, "Bearer ")
		if token != "qa-challenge-token" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid token"})
			return
		}
		c.Next()
	}
}

// listServices handles GET /api/v1/services
// BUG-003: total_pages uses integer division (floor) instead of ceiling.
func listServices(c *gin.Context) {
	page, err := strconv.Atoi(c.DefaultQuery("page", "1"))
	if err != nil || page < 1 {
		page = 1
	}
	perPage, err := strconv.Atoi(c.DefaultQuery("per_page", "10"))
	if err != nil || perPage < 1 || perPage > 100 {
		perPage = 10
	}

	total := len(serviceStore)
	offset := (page - 1) * perPage
	end := offset + perPage
	if end > total {
		end = total
	}

	var pageItems []Service
	if offset < total {
		pageItems = serviceStore[offset:end]
	} else {
		pageItems = []Service{}
	}

	// BUG-003: should use math.Ceil or integer ceiling arithmetic.
	// Correct: int(math.Ceil(float64(total) / float64(perPage)))
	totalPages := int(math.Floor(float64(total) / float64(perPage)))

	c.JSON(http.StatusOK, PaginatedResponse{
		Data:       pageItems,
		Total:      total,
		Page:       page,
		PerPage:    perPage,
		TotalPages: totalPages,
	})
}

// getService handles GET /api/v1/services/:id
// BUG-001: returns 500 (nil pointer dereference) instead of 404 when service is not found.
func getService(c *gin.Context) {
	id := c.Param("id")
	service := findServiceByID(id)
	// BUG-001: no nil check before dereferencing. When service is nil,
	// the dereference *service panics. gin.Recovery catches the panic
	// and returns 500 Internal Server Error instead of a proper 404.
	// Correct:
	//   if service == nil {
	//       c.JSON(http.StatusNotFound, gin.H{"error": "service not found"})
	//       return
	//   }
	c.JSON(http.StatusOK, *service)
}

// searchServices handles POST /api/v1/services/search
// BUG-002: empty query returns 200 with all results instead of 400.
func searchServices(c *gin.Context) {
	var req struct {
		Query string `json:"query"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid JSON body"})
		return
	}
	// BUG-002: missing empty query validation.
	// Correct:
	//   if strings.TrimSpace(req.Query) == "" {
	//       c.JSON(http.StatusBadRequest, gin.H{"error": "query cannot be empty"})
	//       return
	//   }
	results := filterByQuery(req.Query)
	c.JSON(http.StatusOK, gin.H{
		"results": results,
		"total":   len(results),
		"query":   req.Query,
	})
}

// getRecommendations handles GET /api/v1/services/:id/recommendations.
// This endpoint returns personalized data and should require authentication.
// BUG-005: registered in the public route group — no auth check performed.
func getRecommendations(c *gin.Context) {
	id := c.Param("id")
	service := findServiceByID(id)
	if service == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "service not found"})
		return
	}

	var recommendations []Service
	for _, s := range serviceStore {
		if s.Category == service.Category && s.ID != id {
			recommendations = append(recommendations, s)
		}
	}

	c.JSON(http.StatusOK, gin.H{
		"service_id":      id,
		"recommendations": recommendations,
	})
}

// handleCatalogWebhook handles POST /api/v1/webhooks/catalog.
// BUG-004: reads the HMAC signature header but never validates it.
func handleCatalogWebhook(c *gin.Context) {
	// BUG-004: signature is read but immediately discarded.
	// The correct implementation should call validateHMAC and return 401 on failure.
	signature := c.GetHeader("X-Signature-256")
	slog.Info("webhook received", "signature_present", signature != "")

	var payload map[string]interface{}
	if err := c.ShouldBindJSON(&payload); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid JSON payload"})
		return
	}

	slog.Info("catalog update processed", "fields", len(payload))
	c.JSON(http.StatusOK, gin.H{
		"status":   "accepted",
		"received": time.Now().UTC().Format(time.RFC3339),
	})
}

// validateHMAC verifies that a request body matches the expected HMAC-SHA256 signature.
// This is the correct implementation — it is intentionally not called (BUG-004).
func validateHMAC(body []byte, signature, secret string) bool {
	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write(body)
	expected := "sha256=" + hex.EncodeToString(mac.Sum(nil))
	return hmac.Equal([]byte(signature), []byte(expected))
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	gin.SetMode(gin.ReleaseMode)
	r := gin.New()
	r.Use(gin.Recovery()) // catches panics and returns 500
	r.Use(gin.Logger())

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":    "ok",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
			"version":   "1.0.0",
			"services":  len(serviceStore),
		})
	})

	// Public routes — no authentication required
	public := r.Group("/api/v1")
	{
		public.GET("/services", listServices)
		public.POST("/services/search", searchServices)
		public.GET("/services/:id", getService)
		// BUG-005: this endpoint should be in the protected group below.
		public.GET("/services/:id/recommendations", getRecommendations)
		public.POST("/webhooks/catalog", handleCatalogWebhook)
	}

	// Protected routes — require valid Authorization header
	protected := r.Group("/api/v1")
	protected.Use(authMiddleware())
	{
		// Example of a correctly protected endpoint for reference.
		protected.POST("/services/:id/favorite", func(c *gin.Context) {
			id := c.Param("id")
			service := findServiceByID(id)
			if service == nil {
				c.JSON(http.StatusNotFound, gin.H{"error": "service not found"})
				return
			}
			c.JSON(http.StatusOK, gin.H{
				"message":    "added to favorites",
				"service_id": id,
			})
		})
	}

	slog.Info("catalog API starting", "port", port, "services", len(serviceStore))
	if err := r.Run(":" + port); err != nil {
		slog.Error("server failed to start", "error", err)
		os.Exit(1)
	}
}
