import crypto from "k6/crypto";
import http from "k6/http";
import { check } from "k6";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8080";
const TOKEN = __ENV.AUTH_TOKEN || "qa-challenge-token";
const WEBHOOK_SECRET = __ENV.WEBHOOK_SECRET || "webhook-secret-2024";

export const options = {
  scenarios: {
    health: {
      executor: "constant-arrival-rate",
      rate: 8,
      timeUnit: "1s",
      duration: "45s",
      preAllocatedVUs: 10,
      maxVUs: 30,
      exec: "health",
    },
    list_services: {
      executor: "constant-arrival-rate",
      rate: 10,
      timeUnit: "1s",
      duration: "45s",
      preAllocatedVUs: 15,
      maxVUs: 40,
      exec: "listServices",
    },
    service_detail: {
      executor: "constant-arrival-rate",
      rate: 8,
      timeUnit: "1s",
      duration: "45s",
      preAllocatedVUs: 10,
      maxVUs: 30,
      exec: "serviceDetail",
    },
    search: {
      executor: "constant-arrival-rate",
      rate: 6,
      timeUnit: "1s",
      duration: "45s",
      preAllocatedVUs: 10,
      maxVUs: 30,
      exec: "search",
    },
    recommendations: {
      executor: "constant-arrival-rate",
      rate: 2,
      timeUnit: "1s",
      duration: "45s",
      preAllocatedVUs: 5,
      maxVUs: 15,
      exec: "recommendations",
    },
    webhook: {
      executor: "constant-arrival-rate",
      rate: 1,
      timeUnit: "1s",
      duration: "45s",
      preAllocatedVUs: 3,
      maxVUs: 10,
      exec: "webhook",
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<300", "p(99)<750"],
    "http_req_duration{operation:health}": ["p(95)<150"],
    "http_req_duration{operation:list_services}": ["p(95)<300"],
    "http_req_duration{operation:service_detail}": ["p(95)<250"],
    "http_req_duration{operation:search}": ["p(95)<350"],
    "http_req_duration{operation:recommendations}": ["p(95)<350"],
    "http_req_duration{operation:webhook}": ["p(95)<400"],
    dropped_iterations: ["count==0"],
    checks: ["rate>0.99"],
  },
};

function assertOk(response) {
  check(response, {
    "status is 2xx": (res) => res.status >= 200 && res.status < 300,
    "body is not empty": (res) => Boolean(res.body && res.body.length > 0),
  });
}

function signedWebhookPayload() {
  const body = JSON.stringify({
    event: "service.updated",
    id: "s002",
    source: "k6",
  });
  const signature = crypto.hmac("sha256", WEBHOOK_SECRET, body, "hex");
  return {
    body,
    headers: {
      "Content-Type": "application/json",
      "X-Signature-256": `sha256=${signature}`,
    },
  };
}

export function health() {
  assertOk(http.get(`${BASE_URL}/health`, { tags: { operation: "health" } }));
}

export function listServices() {
  assertOk(
    http.get(`${BASE_URL}/api/v1/services?page=1&per_page=10`, {
      tags: { operation: "list_services" },
    }),
  );
}

export function serviceDetail() {
  assertOk(
    http.get(`${BASE_URL}/api/v1/services/s002`, {
      tags: { operation: "service_detail" },
    }),
  );
}

export function search() {
  assertOk(
    http.post(`${BASE_URL}/api/v1/services/search`, JSON.stringify({ query: "saude" }), {
      headers: { "Content-Type": "application/json" },
      tags: { operation: "search" },
    }),
  );
}

export function recommendations() {
  assertOk(
    http.get(`${BASE_URL}/api/v1/services/s002/recommendations`, {
      headers: { Authorization: `Bearer ${TOKEN}` },
      tags: { operation: "recommendations" },
    }),
  );
}

export function webhook() {
  const payload = signedWebhookPayload();
  assertOk(
    http.post(`${BASE_URL}/api/v1/webhooks/catalog`, payload.body, {
      headers: payload.headers,
      tags: { operation: "webhook" },
    }),
  );
}
