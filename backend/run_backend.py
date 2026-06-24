from __future__ import annotations

import os

try:
    import uvicorn
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Uvicorn is not installed in this Python environment. "
        "Run: python -m pip install -r requirements.txt"
    ) from exc


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("BACKEND_PORT", "8000")))
    reload = os.getenv("RELOAD", "true").lower() in {"1", "true", "yes"}
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)
