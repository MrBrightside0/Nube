# SatAirlite Web

Frontend para visualizar calidad del aire usando datos satelitales y modelos de IA. Construido sobre Next.js (App Router) con un enfoque en visualizaciones interactivas, mapas y suscripciones a alertas.

## Tecnologías principales
- Next.js 15 (modo App dir) + React 19 para el enrutado y componentes cliente
- Tailwind CSS v4 para estilos utilitarios globales
- Framer Motion para animaciones de secciones y tarjetas
- Recharts para gráficos de tendencias, predicciones y correlaciones
- React-Leaflet + Leaflet para el mapa interactivo de ciudades

## Estructura relevante
```
app/
├── layout.tsx          # Layout raíz con Navbar y estilos globales
├── page.tsx            # Landing (Hero, About, Stats, Tech, CTA, Footer)
├── alerts/             # Formulario de suscripción a alertas
├── dashboard/          # Panel con zonas de Monterrey y visualizaciones IA
├── map/                # Mapa interactivo + resumen y mini-gráfico
├── trends/             # Tendencias históricas y correlación NO₂ ↔ PM2.5
└── components/         # Componentes compartidos (Hero, Navbar, etc.)
public/                 # Assets (video, íconos, imágenes)
```

## Páginas y vistas
- **Home (`/`)**: landing con video, descripción, estadísticas y secciones informativas.
- **Map (`/map`)**: mapa Leaflet de ciudades predefinidas, panel lateral con métricas actuales y un minigráfico de 7 días.
- **Dashboard (`/dashboard`)**: selector de zona dentro de Monterrey y contaminante; muestra métricas actuales, predicción IA a 30 días y análisis estacional.
- **Trends (`/trends`)**: histórico de 7 días para PM2.5 y NO₂, más diagrama de dispersión y coeficiente de correlación.
- **Alerts (`/alerts`)**: formulario para registrar alertas por email o WhatsApp, asociado a una ciudad.

> Nota: `app/components/Insights.js` contiene un prototipo de sección de insights que consulta endpoints de desarrollo (`http://127.0.0.1:5000`) y no se usa actualmente en las rutas.

## Integración con la API
Toda la comunicación productiva usa `process.env.NEXT_PUBLIC_API_URL`. Define esta variable en un `.env.local` en el root de `web/`:

```
NEXT_PUBLIC_API_URL=https://mi-backend.example.com/api
```

### Contratos esperados
| Endpoint | Método | Uso en frontend | Parámetros | Respuesta esperada |
|----------|--------|-----------------|------------|--------------------|
| `/aq/latest` | GET | `map/page.tsx`, `dashboard/page.tsx` | `lat`, `lon`; opcional `pollutant` | Objeto con `aqi`, `pm25`, `no2`, `wind`; opcional `pm10`, `sources` (array). Ejemplo: `{ "aqi": 87, "pm25": 14.2, "no2": 32.1, "wind": 6.5, "sources": ["TEMPO"] }` |
| `/aq/trends` | GET | `map/page.tsx`, `trends/page.tsx` | `lat`, `lon`, `days` | Objeto `{ "series": [ { "ts": "2024-05-01T00:00Z", "pm25": 12.5, "no2": 28.1 }, ... ], "correlation": 0.63 }`. El campo `correlation` se usa solo en Trends. |
| `/ai/predict` | GET | `dashboard/page.tsx` | `lat`, `lon`, `pollutant`, `days` (30) | Objeto `{ "predictions": [ { "ds": "2024-05-02", "yhat": 17.2 }, ... ] }`. Se aceptan claves `ds` o `ts` en cada punto. |
| `/ai/seasonal` | GET | `dashboard/page.tsx` | `lat`, `lon`, `pollutant` | Objeto con `trend` (array de `{ "ts": "2024-05-01", "value": 15.3 }`). El frontend ignora otros campos. |
| `/alerts/subscribe` | POST | `alerts/page.tsx` | Body JSON `{ "contact": string, "preferences": { "type": "email"\|"whatsapp", "city": string, "lat": number, "lon": number } }` | Se espera un `200 OK`/`201 Created`. El frontend solo verifica `res.ok`. |

### Consideraciones adicionales
- Errores de red se capturan con `console.error`, no hay estados de error visibles salvo en Alerts.
- Para `dashboard`, la selección inicial es la zona "Universidad" con contaminante `pm10`. Cambios disparan los tres `fetch` en paralelo.
- `map/page.tsx` fuerza el remonte del mapa cambiando la `key` cuando se selecciona una ciudad (`lat-lon`).

## Puesta en marcha local
1. Instala dependencias: `npm install`.
2. Crea `.env.local` con `NEXT_PUBLIC_API_URL` apuntando al backend.
3. Ejecuta `npm run dev` para levantar en `http://localhost:3000`.
4. Si usas el mapa, asegúrate de que `leaflet/dist/leaflet.css` esté disponible (se importa en `app/globals.css`).

## Estilos y componentes
- Tailwind CSS v4 se importa globalmente (`app/globals.css`). Puedes añadir utilidades personalizadas o animaciones ahí.
- El layout global (`app/layout.tsx`) agrega `Navbar` fijo con blur al hacer scroll y define la tipografía `Poppins` vía `next/font`.
- Los gráficos usan Recharts y esperan datos ya preformateados (no realizan cálculos adicionales).

## Próximos pasos sugeridos
- Definir manejo de errores y estados vacíos más ricos (skeletons, mensajes descriptivos).
- Extraer configuraciones de zonas/ciudades a un módulo compartido si se comparten con el backend.
- Eliminar o alinear el componente `Insights` con la configuración de API actual para evitar confusiones.
