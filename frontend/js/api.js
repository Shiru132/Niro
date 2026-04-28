const API_URL = "http://127.0.0.1:8000/farm";

async function runFarm() {
  const res = await fetch(`${API_URL}/run`, {
    method: "POST"
  });

  if (!res.ok) {
    throw new Error("API error: " + res.status);
  }

  return res.json();
}

async function getStatus() {
  const res = await fetch(`${API_URL}/status`);
  return res.json();
}
async function runGarden(pid) {
  const res = await fetch(`${API_URL}/garden?pid=${pid}`, {
    method: "POST"
  });
  return res.json();
}