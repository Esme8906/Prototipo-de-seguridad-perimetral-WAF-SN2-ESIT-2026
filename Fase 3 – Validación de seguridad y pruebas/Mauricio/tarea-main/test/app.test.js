import test, { after, before } from "node:test";
import assert from "node:assert/strict";
import app from "../src/app.js";

let server;
let baseUrl;

before(async () => {
  server = app.listen(0, "127.0.0.1");
  await new Promise((resolve) => server.once("listening", resolve));
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

after(() => new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve())));

test("arranca el servidor de prueba", async () => {
  const response = await fetch(baseUrl);
  assert.equal(response.status, 200);
  assert.match(await response.text(), /Universidad Nova Digital/);
});

test("healthcheck informa que el servicio está activo", async () => {
  const response = await fetch(`${baseUrl}/healthcheck`);
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { status: "ok", application: "WAF Shield Cloud" });
});

test("search requiere consulta y devuelve resultado simulado", async () => {
  const missing = await fetch(`${baseUrl}/search`);
  assert.equal(missing.status, 400);

  const found = await fetch(`${baseUrl}/search?q=portal`);
  const body = await found.json();
  assert.equal(found.status, 200);
  assert.equal(body.query, "portal");
  assert.equal(body.results.length, 1);
});

test("comments valida entrada y conserva una consulta durante la ejecución", async () => {
  const empty = await fetch(`${baseUrl}/comments`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ comment: " " }),
  });
  assert.equal(empty.status, 400);

  const accepted = await fetch(`${baseUrl}/comments`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ comment: "Comentario ficticio" }),
  });
  assert.equal(accepted.status, 201);
  const body = await accepted.json();
  assert.match(body.message, /temporalmente/);
  assert.equal(body.entry.comment, "Comentario ficticio");
  assert.ok(body.entry.timestamp);
});

test("login valida credenciales ficticias y dashboard requiere una sesión", async () => {
  const missingSession = await fetch(`${baseUrl}/dashboard`);
  assert.equal(missingSession.status, 401);

  const invalidLogin = await fetch(`${baseUrl}/login`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: "demo@example.test", password: "dato-ficticio" }),
  });
  assert.equal(invalidLogin.status, 401);

  const login = await fetch(`${baseUrl}/login`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: "estudiante@nova.edu", password: "Nova2026!" }),
  });
  assert.equal(login.status, 200);
  const session = await login.json();
  assert.equal(session.authenticated, true);
  assert.ok(session.token);

  const dashboard = await fetch(`${baseUrl}/dashboard`, {
    headers: { Authorization: `Bearer ${session.token}` },
  });
  assert.equal(dashboard.status, 200);
  assert.equal((await dashboard.json()).user.role, "estudiante");
});

test("admin permanece restringida por la aplicación", async () => {
  const admin = await fetch(`${baseUrl}/admin`);
  assert.equal(admin.status, 403);
});
