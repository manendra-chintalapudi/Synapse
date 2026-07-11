/* ============================================================================
 * Synapse FRONTEND runtime config.
 *
 * This is a static site (plain HTML/JS — no Vite/Next build step), so the backend
 * URL is injected here rather than through a bundler env var.
 *
 * Set SYNAPSE_API_URL to your deployed backend origin when the frontend (Vercel)
 * and backend (Railway) live on different domains, e.g.
 *     window.SYNAPSE_API_URL = "https://synapse-backend.up.railway.app";
 *
 * Leave it "" to call the SAME origin that served this page — correct for local
 * dev, where the FastAPI backend also serves the frontend.
 *
 * See .env.example (SYNAPSE_API_URL) for the documented variable.
 * ==========================================================================*/
window.SYNAPSE_API_URL = "";
