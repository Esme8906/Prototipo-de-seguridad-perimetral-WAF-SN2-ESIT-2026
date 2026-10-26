const $ = (selector) => document.querySelector(selector);

function showResponse(target, payload, ok = true) {
  target.textContent = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
  target.className = `response ${ok ? "success" : "error"}`;
}

async function request(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  return { response, data };
}

$("#health-button").addEventListener("click", async () => {
  const title = $("#status-title");
  const detail = $("#status-detail");
  title.textContent = "Consultando el servicio…";
  try {
    const { response, data } = await request("/healthcheck");
    title.textContent = response.ok ? "Portal disponible" : "No se pudo consultar el portal";
    detail.textContent = response.ok ? "El portal está respondiendo correctamente." : JSON.stringify(data);
  } catch {
    title.textContent = "No se pudo conectar";
    detail.textContent = "Verifica que el servidor local esté ejecutándose.";
  }
});

$("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const target = $("#login-response");
  try {
    const { response, data } = await request("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: $("#login-email").value, password: $("#login-password").value }),
    });
    showResponse(target, { httpStatus: response.status, ...data }, response.ok);
  } catch {
    showResponse(target, "No se pudo conectar con el servidor.", false);
  }
  event.target.reset();
});

$("#search-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = $("#search-query").value.trim();
  const target = $("#search-response");
  try {
    const { response, data } = await request(`/search?q=${encodeURIComponent(query)}`);
    showResponse(target, data, response.ok);
  } catch {
    showResponse(target, "No se pudo conectar con el servidor.", false);
  }
});

$("#comment-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const comment = $("#comment-text").value.trim();
  const target = $("#comment-response");
  try {
    const { response, data } = await request("/comments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ comment }),
    });
    showResponse(target, data, response.ok);
    if (response.ok) event.target.reset();
  } catch {
    showResponse(target, "No se pudo conectar con el servidor.", false);
  }
});

$("#admin-button").addEventListener("click", async () => {
  const target = $("#admin-response");
  try {
    const { response, data } = await request("/admin");
    showResponse(target, { httpStatus: response.status, ...data }, response.ok);
  } catch {
    showResponse(target, "No se pudo conectar con el servidor.", false);
  }
});
