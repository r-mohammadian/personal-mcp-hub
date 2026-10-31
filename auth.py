"""auth.py – Anmeldung am persönlichen Microsoft-Konto (outlook.de) mit verschlüsseltem Token-Cache.

- Der Token-Cache liegt AUSSERHALB des Repos: %LOCALAPPDATA%\\personal-mcp-hub\\token_cache.bin
- Unter Windows wird er mit DPAPI verschlüsselt (nur dieser Windows-Benutzer auf diesem Rechner kann ihn lesen).
- Beim ersten Start öffnet sich der Browser zur Anmeldung, danach läuft es still (ohne erneute Anmeldung).
"""

import os
from pathlib import Path

import msal
from msal_extensions import PersistedTokenCache, build_encrypted_persistence

# Öffentliche Client-ID der App-Registrierung (kein Geheimnis, Public Client ohne Secret)
CLIENT_ID = "ef8cac19-0e56-4657-aa67-f3ba16b62cc5"
AUTHORITY = "https://login.microsoftonline.com/consumers"
# offline_access fügt MSAL automatisch hinzu – nicht selbst eintragen
SCOPES = ["User.Read", "Mail.Read"]

CACHE_DIR = Path(os.environ["LOCALAPPDATA"]) / "personal-mcp-hub"
CACHE_FILE = CACHE_DIR / "token_cache.bin"


def _build_app() -> msal.PublicClientApplication:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    persistence = build_encrypted_persistence(str(CACHE_FILE))
    cache = PersistedTokenCache(persistence)
    return msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)


def get_token() -> str:
    """Gibt ein gültiges Access-Token zurück – erst still aus dem Cache, sonst interaktiv."""
    app = _build_app()

    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            return result["access_token"]

    result = app.acquire_token_interactive(SCOPES)
    if "access_token" not in result:
        raise RuntimeError(f"Anmeldung fehlgeschlagen: {result.get('error_description', result)}")
    return result["access_token"]


if __name__ == "__main__":
    token = get_token()
    # Token selbst NIE ausgeben – nur zeigen, dass es geklappt hat
    print("OK – Token erhalten (Länge:", len(token), "Zeichen)")
    print("Cache-Datei:", CACHE_FILE)
