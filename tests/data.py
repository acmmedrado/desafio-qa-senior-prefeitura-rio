BENEFITS_CATEGORY = "beneficios"
HEALTH_CATEGORY = "saude"
EXPECTED_CATEGORIES = {
    "assistencia_social",
    BENEFITS_CATEGORY,
    "educacao",
    "empresas",
    "habitacao",
    "meio_ambiente",
    HEALTH_CATEGORY,
    "trabalho",
    "transporte",
}

FAVORITE_SERVICE_TITLE = "Cartão Rio"
FAVORITE_SERVICE_ID = "s001"
VACCINATION_SERVICE_ID = "s002"
VACCINATION_SERVICE_TITLE = "Vacinação Gratuita"
FAMILY_SERVICE_ID = "s011"
SCHOOL_ENROLLMENT_SERVICE_ID = "s003"
BUSINESS_OPENING_SERVICE_ID = "s009"
BUS_PASS_SERVICE_ID = "s006"
HEALTH_SERVICE_IDS = {"s002", "s010"}
BENEFITS_SERVICE_IDS = {"s001", "s011"}
UNKNOWN_SERVICE_ID = "s999"

BUSINESS_NEED_QUERY = "abrir comercio"
BUS_QUERY = "onibus"
FAMILY_QUERY = "familia"
HEALTH_QUERY = "saude"
HEALTH_QUERY_UPPER = "SAUDE"
NO_MATCH_QUERY = "termo-sem-correspondencia"
SCHOOL_ENROLLMENT_NEED_QUERY = "matricular filho"
SPACED_HEALTH_QUERY = "  saude  "
VACCINATION_QUERY = "vacina"
VACCINATION_QUERY_WITHOUT_ACCENT = "vacinacao"

SERVICE_DELETED_EVENT = "service.deleted"
SERVICE_UPDATED_EVENT = "service.updated"
