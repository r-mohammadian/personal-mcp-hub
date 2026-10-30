import msal
import requests
from datetime import datetime

CLIENT_ID = "ef8cac19-0e56-4657-aa67-f3ba16b62cc5"
AUTHORITY = "https://login.microsoftonline.com/consumers"
SCOPES = ["Mail.Read", "User.Read"]  # offline_access fuegt MSAL automatisch hinzu

app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
result = app.acquire_token_interactive(scopes=SCOPES)

if "access_token" not in result:
    print("Login fehlgeschlagen:", result.get("error"), result.get("error_description"))
    raise SystemExit(1)

headers = {"Authorization": f"Bearer {result['access_token']}"}

me = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers, timeout=30).json()
print("Angemeldet als:", me.get("userPrincipalName") or me.get("mail"))

url = ("https://graph.microsoft.com/v1.0/me/messages"
       "?$top=5&$select=subject,from,receivedDateTime&$orderby=receivedDateTime desc")
r = requests.get(url, headers=headers, timeout=30)
r.raise_for_status()

for m in r.json()["value"]:
    sender = m.get("from", {}).get("emailAddress", {}).get("address", "?")
    zeit = datetime.fromisoformat(m["receivedDateTime"].replace("Z", "+00:00")).astimezone()
    print(zeit.strftime("%d.%m.%Y %H:%M"), "|", sender, "|", m.get("subject"))