const API_BASE_URL = "http://127.0.0.1:8000";

export async function getCurrentCyclone() {
  const response = await fetch(
    `${API_BASE_URL}/cyclone/current`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch current cyclone");
  }

  return response.json();
}

export async function getAnalyticsSummary() {
  const response = await fetch(
    `${API_BASE_URL}/analytics/summary`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch analytics");
  }

  return response.json();
}

export async function getCycloneAnalytics(cycloneId) {
  const response = await fetch(
    `${API_BASE_URL}/analytics/cyclone/${cycloneId}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch cyclone analytics");
  }

  return response.json();
}

export async function getAdvisoryLanguages() {
  const response = await fetch(
    `${API_BASE_URL}/advisory/languages`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch advisory languages");
  }

  return response.json();
}

export async function generateAlert(data) {
  const response = await fetch(
    `${API_BASE_URL}/generate-alert`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to generate alert");
  }

  return response.json();
}