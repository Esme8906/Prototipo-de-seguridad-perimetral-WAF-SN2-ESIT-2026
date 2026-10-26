# Portal Universidad Nova Digital - prototipo de prueba

Portal universitario ficticio para representar el servicio web que protegerá el proyecto WAF Shield Cloud. Está hecho con Node.js y Express e incluye rutas de demostración. No es el sitio oficial de una universidad, no utiliza base de datos y no conserva los datos enviados. El WAF aún no está conectado.

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
| `POST /comments` | Valida un comentario y confirma recepción sin guardarlo. |
| `POST /login` | Informa que la autenticación real no está configurada. No envíes contraseñas reales. |
| `GET /admin` | Devuelve `403` como ruta restringida de demostración. |

## Pruebas automatizadas

```bash
npm test
```

Las pruebas verifican que la aplicación arranque y que las rutas respondan como se espera. El `403` de `/admin` lo devuelve Express como comportamiento de muestra; no es un bloqueo del WAF. Estas pruebas tampoco sustituyen la validación del WAF. Ejecuta pruebas de seguridad únicamente contra el entorno de prueba autorizado por el equipo.

## Antes de compartir

No compartas `node_modules`, `.env`, claves de servicio ni credenciales. El repositorio incluye `.gitignore` para excluir dependencias y archivos de entorno.
