const $ = (selector) => document.querySelector(selector);

function showResponse(target, payload, ok = true) {
  target.textContent = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
  target.className = `response ${ok ? "success" : "error"}`;
}

function responsePayload(response, data) {
  return { httpStatus: response.status, response: data };
}

async function request(url, options) {
  const response = await fetch(url, options);
  const contentType = response.headers.get("content-type") || "";
  const body = await response.text();
  let data = body;

  if (contentType.includes("application/json")) {
    try {
      data = JSON.parse(body);
    } catch {
      data = { error: "El servidor indicó JSON, pero devolvió una respuesta inválida." };
    }
  }

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
    if (!response.ok || !data.token) {
      showResponse(target, responsePayload(response, data), false);
      return;
    }

    const dashboard = await request("/dashboard", {
      headers: { Authorization: `Bearer ${data.token}` },
    });
    showResponse(target, {
      httpStatus: response.status,
      message: data.message,
      user: data.user,
      dashboard: dashboard.data,
    }, dashboard.response.ok);
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
    showResponse(target, responsePayload(response, data), response.ok);
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
    showResponse(target, responsePayload(response, data), response.ok);
    if (response.ok) event.target.reset();
  } catch {
    showResponse(target, "No se pudo conectar con el servidor.", false);
  }
});

$("#admin-button").addEventListener("click", async () => {
  const target = $("#admin-response");
  try {
    const { response, data } = await request("/admin");
    showResponse(target, responsePayload(response, data), response.ok);
  } catch {
    showResponse(target, "No se pudo conectar con el servidor.", false);
  }
});
