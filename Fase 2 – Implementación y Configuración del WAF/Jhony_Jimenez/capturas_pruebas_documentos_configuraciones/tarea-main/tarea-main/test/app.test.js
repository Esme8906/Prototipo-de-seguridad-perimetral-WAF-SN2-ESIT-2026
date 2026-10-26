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

test("comments valida entrada y no persiste datos", async () => {
  const empty = await fetch(`${baseUrl}/comments`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ comment: " " }),
  });
  assert.equal(empty.status, 400);

  const accepted = await fetch(`${baseUrl}/comments`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ comment: "Comentario ficticio" }),
  });
  assert.equal(accepted.status, 201);
  assert.match((await accepted.json()).message, /no se guardó/);
});

test("admin permanece restringida y login aclara que no hay autenticación real", async () => {
  const admin = await fetch(`${baseUrl}/admin`);
  assert.equal(admin.status, 403);

  const login = await fetch(`${baseUrl}/login`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: "demo@example.test", password: "dato-ficticio" }),
  });
  assert.equal(login.status, 501);
});
