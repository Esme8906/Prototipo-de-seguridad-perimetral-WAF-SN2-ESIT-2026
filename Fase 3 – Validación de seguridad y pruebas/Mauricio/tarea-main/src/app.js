import express from "express";
import path from "node:path";
import { fileURLToPath } from "node:url";

const app = express();
const here = path.dirname(fileURLToPath(import.meta.url));

app.disable("x-powered-by");
app.use(express.json({ limit: "20kb" }));
app.use(express.static(path.join(here, "../public")));

// Cuentas ficticias exclusivas para las pruebas del prototipo.
// No representan usuarios reales ni deben reutilizarse fuera del laboratorio.
const DEMO_USERS = [
  {
    email: "estudiante@nova.edu",
    password: "Nova2026!",
    name: "Mauricio Martínez",
    role: "estudiante",
    career: "Ingeniería Eléctrica / Servicios en la Nube",
  },
  {
    email: "admin@nova.edu",
    password: "AdminNova2026!",
    name: "Administrador Campus",
    role: "admin",
    career: "Dirección TI",
  },
];

// Los datos de demostración se conservan solo mientras Node.js está encendido.
const activeSessions = new Map();
const recentComments = [];

function getBearerToken(authorization = "") {
  const match = /^Bearer\s+(.+)$/i.exec(authorization);
  return match?.[1]?.trim() ?? "";
}

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
      {
        title: "Resultado académico",
        description: `Coincidencia encontrada en el catálogo para: ${query}`,
      },
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

  const entry = {
    id: recentComments.length + 1,
    comment,
    timestamp: new Date().toISOString(),
  };
  recentComments.push(entry);
  if (recentComments.length > 10) recentComments.shift();

  return res.status(201).json({
    message: "Consulta registrada temporalmente para demostración.",
    entry,
  });
});

app.post("/login", (req, res) => {
  const email = typeof req.body?.email === "string" ? req.body.email.trim().toLowerCase() : "";
  const password = typeof req.body?.password === "string" ? req.body.password : "";
  if (!email || !password) {
    return res.status(400).json({ error: "Completa correo y contraseña." });
  }

  const user = DEMO_USERS.find((candidate) => candidate.email === email && candidate.password === password);
  if (!user) {
    return res.status(401).json({
      authenticated: false,
      error: "Acceso denegado: correo o contraseña incorrectos.",
    });
  }

  const token = crypto.randomUUID();
  activeSessions.set(token, user);

  return res.status(200).json({
    authenticated: true,
    message: `Bienvenido al Campus Virtual, ${user.name}.`,
    user: {
      name: user.name,
      email: user.email,
      role: user.role,
      career: user.career,
    },
    token,
  });
});

app.get("/dashboard", (req, res) => {
  const token = getBearerToken(req.headers.authorization);
  const user = activeSessions.get(token);
  if (!user) {
    return res.status(401).json({ error: "Sesión no válida o token ausente." });
  }

  return res.json({
    user: { name: user.name, role: user.role, career: user.career },
    status: "Activo - Ciclo II 2026",
    courses: [
      "Arquitectura Cloud y Seguridad Perimetral",
      "Sistemas Eléctricos de Potencia",
      "Redes de Distribución",
    ],
  });
});

app.get("/admin", (_req, res) => {
  res.status(403).json({ error: "Acceso restringido a nivel de aplicación." });
});

app.use((err, _req, res, _next) => {
  if (err instanceof SyntaxError && "body" in err) {
    return res.status(400).json({ error: "El cuerpo JSON no es válido." });
  }
  console.error(err);
  return res.status(500).json({ error: "Error interno del servidor." });
});

export default app;
