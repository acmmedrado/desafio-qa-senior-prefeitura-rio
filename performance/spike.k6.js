import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8080";

export const options = {
  scenarios: {
    sudden_public_demand: {
      executor: "ramping-vus",
      stages: [
        { duration: "15s", target: 20 },
        { duration: "15s", target: 150 },
        { duration: "30s", target: 150 },
        { duration: "15s", target: 20 },
        { duration: "15s", target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.02"],
    http_req_duration: ["p(95)<500", "p(99)<1000"],
    checks: ["rate>0.98"],
  },
};

export default function () {
  const responses = http.batch([
    ["GET", `${BASE_URL}/health`],
    ["GET", `${BASE_URL}/api/v1/services?page=1&per_page=10`],
    [
      "POST",
      `${BASE_URL}/api/v1/services/search`,
      JSON.stringify({ query: "saude" }),
      { headers: { "Content-Type": "application/json" } },
    ],
  ]);

  for (const response of responses) {
    check(response, {
      "status is 2xx": (res) => res.status >= 200 && res.status < 300,
    });
  }
  sleep(1);
}
