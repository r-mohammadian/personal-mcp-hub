# personal-mcp-hub

Ein eigener, lokaler **MCP-Server** (Model Context Protocol), der einer KI wie **Claude** lesenden Zugriff auf mein persönliches Outlook-Postfach gibt – über **Microsoft Graph**, mit Anmeldung über **Entra ID** und nach dem **Least-Privilege-Prinzip**.

> Lernprojekt im Rahmen meines Wegs Richtung Systemadministration / M365.

## Was es kann

| Tool | Beschreibung |
| --- | --- |
| `neueste_mails` | Zeigt die neuesten E-Mails aus dem Posteingang (1–25) |
| `mails_suchen` | Sucht E-Mails nach einem Stichwort (Betreff, Absender, Text) |

Beide Tools **lesen nur** – kein Senden, Löschen oder Verschieben.

## Architektur

```
Claude Desktop ──stdio──> server.py ──Token──> Microsoft Graph ──> Outlook-Postfach
                              │
                           auth.py ──> Entra ID (Browser-Login nur beim ersten Mal)
                              │
                    token_cache.bin (DPAPI-verschlüsselt, außerhalb des Repos)
```

## Sicherheit

- **App-Registrierung in Entra ID** als Public Client, **ohne Client-Secret**
- **Delegierte Berechtigungen** nur `Mail.Read` und `User.Read` (Least Privilege)
- **Token-Cache** mit `msal-extensions` per **Windows DPAPI** verschlüsselt, gespeichert unter `%LOCALAPPDATA%\personal-mcp-hub\` – also **nie im Git-Repository**
- Tokens werden nie ausgegeben oder geloggt

## Technik

- Python 3.12, `msal`, `msal-extensions`, `requests` – Versionen in `requirements.txt` festgelegt
- `mcp` (Python SDK, FastMCP) – bewusst auf Version `<2` gepinnt, weil 2.x die API geändert hat
- Microsoft Graph REST API (`/me/messages`)
- Claude Desktop als MCP-Client (lokal, stdio)

## Installation (Windows)

```powershell
git clone https://github.com/r-mohammadian/personal-mcp-hub.git
cd personal-mcp-hub
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python auth.py        # einmalige Anmeldung im Browser
```

Danach in Claude Desktop unter **Einstellungen → Entwickler → Konfiguration bearbeiten** eintragen:

```json
"mcpServers": {
  "personal-mcp-hub": {
    "command": "C:\\Pfad\\zu\\personal-mcp-hub\\.venv\\Scripts\\python.exe",
    "args": ["C:\\Pfad\\zu\\personal-mcp-hub\\server.py"]
  }
}
```

## Projektverlauf

| Phase | Inhalt | Stand |
| --- | --- | --- |
| 0 | App-Registrierung in Entra ID, Berechtigungen | erledigt |
| 1 | Erster Login-Test mit MSAL (Testskript, inzwischen entfernt) | erledigt |
| 2 | Verschlüsselter Token-Cache + MCP-Server | erledigt |
| 3 | Anbindung an Claude Desktop | erledigt |
| 4 | Idee: Betrieb in Azure + Nutzung vom Handy | offen |

## Was ich gelernt habe

- **Entra ID App-Registrierung**: Unterschied zwischen Public Client (ohne Secret) und Confidential Client – und warum für eine lokale App kein Secret nötig ist
- **Delegierte Berechtigungen und Least Privilege**: nur so viel Zugriff wie nötig (`Mail.Read` statt `Mail.ReadWrite`)
- **OAuth 2.0 / MSAL**: Anmeldung im Browser, Access- und Refresh-Token, stilles Erneuern ohne erneuten Login
- **Sichere Token-Speicherung** mit Windows DPAPI statt Klartext-Datei
- **Microsoft Graph REST API**: Anfragen, Filter und Suche im Postfach
- **Model Context Protocol (MCP)**: wie eine KI über einen lokalen Server kontrolliert auf Daten zugreift
- **Abhängigkeiten festlegen**: eine neue Hauptversion (`mcp` 2.x) hat den Code gebrochen – seitdem sind Versionen gepinnt
- **Git und GitHub**: Commits, `.gitignore` für Secrets und lokale Dateien

## Bewusste Grenzen

- Nur **lesen** – Senden, Löschen oder Verschieben ist absichtlich nicht eingebaut
- Nur **mein eigenes Postfach** – kein Zugriff auf andere Konten, keine Mehrbenutzer-Funktion
- Läuft nur **lokal unter Windows** (DPAPI) – kein Server, kein Cloud-Betrieb (Phase 4 offen)
- Keine automatisierten Tests und keine CI-Pipeline – für ein persönliches Lernprojekt bewusst weggelassen

## Entstehung

Konzept, Einrichtung in Entra ID, Tests und Entscheidungen stammen von mir.
Beim Schreiben des Codes habe ich KI-Unterstützung (Claude) genutzt und jeden Schritt selbst ausgeführt, geprüft und dokumentiert.

## Autor

Rahman Mohammadian – Fachinformatiker für Systemintegration
