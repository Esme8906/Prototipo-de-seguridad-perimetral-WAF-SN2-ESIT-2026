import express from "express";
import path from "node:path";
import { fileURLToPath } from "node:url";

const app = express();
const here = path.dirname(fileURLToPath(import.meta.url));

app.disable("x-powered-by");
app.use(express.json({ limit: "20kb" }));
app.use(express.static(path.join(here, "../public")));

app.get("/healthcheck", (_req, res) => {
  res.json({ status: "ok", application: "WAF Shield Cloud" });
});

app.get("/search", (req, res) => {
  const query = String(req.query.q ?? "").trim();
  if (!query) {
    return res.status(400).json({ error: "Escribe un término para buscar." });
  }

  // Resultado simulado: el prototipo no consulta una base de datos.
  return res.json({
    query,
    results: [
      { title: "Resultado de demostración", description: `Consulta recibida: ${query}` },
    ],
  });
});

app.post("/comments", (req, res) => {
  const comment = typeof req.body?.comment === "string" ? req.body.comment.trim() : "";
  if (!comment) {
    return res.status(400).json({ error: "El comentario no puede estar vacío." });
  }
  if (comment.length > 500) {
    return res.status(413).json({ error: "El comentario supera el límite de 500 caracteres." });
  }

  // No guarda comentarios: solo confirma la recepción para pruebas.
  return res.status(201).json({ message: "Comentario de prueba recibido; no se guardó." });
});

app.post("/login", (req, res) => {
  const email = typeof req.body?.email === "string" ? req.body.email.trim() : "";
  const password = typeof req.body?.password === "string" ? req.body.password : "";
  if (!email || !password) {
    return res.status(400).json({ error: "Completa correo y contraseña de prueba." });
  }

  // No existe autenticación real en este prototipo; nunca valida ni conserva credenciales.
  return res.status(501).json({ message: "Autenticación real no configurada en este prototipo." });
});

app.get("/admin", (_req, res) => {
  res.status(403).json({ error: "Acceso de demostración denegado." });
});

app.use((err, _req, res, _next) => {
  if (err instanceof SyntaxError && "body" in err) {
    return res.status(400).json({ error: "El cuerpo JSON no es válido." });
  }
  console.error(err);
  return res.status(500).json({ error: "Error interno del servidor." });
});

export default app;
