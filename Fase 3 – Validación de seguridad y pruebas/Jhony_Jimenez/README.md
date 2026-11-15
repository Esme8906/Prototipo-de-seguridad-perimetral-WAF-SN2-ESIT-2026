# Portal Universidad Nova Digital - prototipo de prueba

Portal universitario ficticio para representar el servicio web que protegerá el proyecto WAF Shield Cloud. Está hecho con Node.js y Express e incluye rutas de demostración. No es el sitio oficial de una universidad, no utiliza base de datos y el WAF aún no está conectado.

## Requisitos

- Node.js 20 o posterior
- npm

## Ejecutar localmente

```bash
npm install
npm run dev
```

Abre `http://localhost:3000`. Para detener el servidor, usa `Ctrl+C` en la terminal. Para ejecución normal sin recarga automática, usa `npm start`.

## Rutas incluidas

| Método y ruta | Comportamiento de demostración |
| --- | --- |
| `GET /` | Sirve el portal ficticio de Universidad Nova Digital. |
| `GET /healthcheck` | Devuelve el estado del servicio. |
| `GET /search?q=...` | Devuelve un resultado simulado; no consulta una base de datos. |
| `POST /comments` | Valida y conserva hasta diez comentarios solamente en memoria mientras la aplicación sigue encendida. |
| `POST /login` | Valida una cuenta ficticia de laboratorio y crea una sesión temporal. No envíes contraseñas reales. |
| `GET /dashboard` | Requiere un token Bearer de una sesión temporal válida. |
| `GET /admin` | Devuelve `403` como restricción creada por la aplicación. |

## Pruebas automatizadas

```bash
npm test
```

Las pruebas verifican que la aplicación arranque y que las rutas respondan como se espera. El `403` de `/admin` lo devuelve Express como comportamiento de muestra; no es un bloqueo del WAF. Las sesiones y comentarios se pierden al reiniciar Node.js. Estas pruebas tampoco sustituyen la validación del WAF. Ejecuta pruebas de seguridad únicamente contra el entorno de prueba autorizado por el equipo.

## Antes de compartir

No compartas `node_modules`, `.env`, claves de servicio ni credenciales reales. Las cuentas del código son exclusivamente ficticias para las pruebas del prototipo. El repositorio incluye `.gitignore` para excluir dependencias y archivos de entorno.
