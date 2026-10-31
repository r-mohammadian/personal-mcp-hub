"""server.py – MCP-Server (nur lesen) für die Outlook-Mails des persönlichen Microsoft-Kontos.

Zwei Werkzeuge (Tools), beide NUR LESEN:
- neueste_mails: die neuesten Mails aus dem Posteingang
- mails_suchen:  Mails nach einem Stichwort suchen

Kein Senden, kein Löschen, kein Verschieben. Die Anmeldung kommt aus auth.py (verschlüsselter Token-Cache).
"""

import requests
from mcp.server.fastmcp import FastMCP

from auth import get_token

GRAPH = "https://graph.microsoft.com/v1.0"
SELECT = "subject,from,receivedDateTime,bodyPreview"

mcp = FastMCP("personal-mcp-hub")


def _get(url: str, params: dict) -> list:
    """Fragt Microsoft Graph ab und gibt die Liste der Mails zurück."""
    headers = {"Authorization": f"Bearer {get_token()}"}
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("value", [])


def _format(messages: list) -> str:
    """Macht aus den Mails einen gut lesbaren Text."""
    lines = []
    for m in messages:
        sender = m.get("from", {}).get("emailAddress", {}).get("address", "?")
        datum = m.get("receivedDateTime", "")[:16].replace("T", " ")
        betreff = m.get("subject", "") or "(ohne Betreff)"
        vorschau = (m.get("bodyPreview", "") or "")[:200].replace("\n", " ")
        lines.append(f"{datum} | {sender} | {betreff}\n    {vorschau}")
    return "\n".join(lines) if lines else "Keine Mails gefunden."


@mcp.tool()
def neueste_mails(anzahl: int = 5) -> str:
    """Zeigt die neuesten E-Mails aus dem Posteingang (nur lesen). anzahl: 1 bis 25."""
    anzahl = max(1, min(anzahl, 25))
    msgs = _get(
        f"{GRAPH}/me/mailFolders/inbox/messages",
        {"$top": anzahl, "$select": SELECT, "$orderby": "receivedDateTime desc"},
    )
    return _format(msgs)


@mcp.tool()
def mails_suchen(suchbegriff: str, anzahl: int = 10) -> str:
    """Sucht E-Mails nach einem Stichwort in Betreff, Absender oder Text (nur lesen). anzahl: 1 bis 25."""
    anzahl = max(1, min(anzahl, 25))
    begriff = suchbegriff.replace('"', "")
    msgs = _get(
        f"{GRAPH}/me/messages",
        {"$search": f'"{begriff}"', "$top": anzahl, "$select": SELECT},
    )
    return _format(msgs)


if __name__ == "__main__":
    # Startet den Server im MCP-Modus (stdio) – wird später von Claude Desktop gestartet.
    mcp.run()
