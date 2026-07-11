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
window.SYNAPSE_API_URL = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname)
  ? ""
  : "https://web-production-a9e7.up.railway.app";

window.SYNAPSE_SUPABASE_URL = "https://oybxogkpkkzywmmivkzy.supabase.co";
window.SYNAPSE_SUPABASE_PUBLISHABLE_KEY = "sb_publishable_Sz8R-hi_ccyAXoSjSeJu4g_xmv17UeE";
