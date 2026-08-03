import crypto from "k6/crypto";
import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8080";
const TOKEN = __ENV.AUTH_TOKEN || "qa-challenge-token";
const WEBHOOK_SECRET = __ENV.WEBHOOK_SECRET || "webhook-secret-2024";

export const options = {
  scenarios: {
    municipal_catalog_load: {
      executor: "ramping-vus",
      stages: [
        { duration: "30s", target: 20 },
        { duration: "1m", target: 50 },
        { duration: "30s", target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<300", "p(99)<750"],
    checks: ["rate>0.99"],
  },
};

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

export default function () {
  const endpoints = [
    () => http.get(`${BASE_URL}/health`),
    () => http.get(`${BASE_URL}/api/v1/services?page=1&per_page=10`),
    () => http.get(`${BASE_URL}/api/v1/services/s002`),
    () =>
      http.post(
        `${BASE_URL}/api/v1/services/search`,
        JSON.stringify({ query: "saude" }),
        { headers: { "Content-Type": "application/json" } },
      ),
    () =>
      http.get(`${BASE_URL}/api/v1/services/s002/recommendations`, {
        headers: { Authorization: `Bearer ${TOKEN}` },
      }),
    () => {
      const payload = signedWebhookPayload();
      return http.post(`${BASE_URL}/api/v1/webhooks/catalog`, payload.body, {
        headers: payload.headers,
      });
    },
  ];

  const response = endpoints[Math.floor(Math.random() * endpoints.length)]();
  check(response, {
    "status is 2xx": (res) => res.status >= 200 && res.status < 300,
    "body is not empty": (res) => Boolean(res.body && res.body.length > 0),
  });
  sleep(1);
}
