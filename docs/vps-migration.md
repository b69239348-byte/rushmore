# Rushmore Backend → Hetzner VPS Migration

**VPS:** 178.104.249.211 (Ubuntu 24.04, 4GB RAM, 75GB Disk)  
**SSH:** `ssh -i ~/.ssh/id_ed25519 root@178.104.249.211`  
**Ziel:** FastAPI-Backend von Railway auf denselben VPS wie den XCEO Woof Bot ziehen.

---

## Kapazität

Der Bot belegt ~54MB RAM, Load average ~0.00. Kein Engpass.  
Deploy-Größe: ~223MB (hauptsächlich `assets/headshots/`).

---

## Was sich ändert

Einzige Code-Änderung: `web/next.config.ts` — Railway-URL durch VPS-IP ersetzen.  
Die Next.js-Rewrites laufen server-seitig → HTTP reicht, kein HTTPS nötig.

---

## Schritt 1 — VPS vorbereiten

```bash
ssh -i ~/.ssh/id_ed25519 root@178.104.249.211

mkdir -p /opt/rushmore
python3 -m venv /opt/rushmore/venv
ufw allow 8080/tcp
```

---

## Schritt 2 — Code + Assets deployen

Vom lokalen Rechner (im Rushmore-Projektordner):

```bash
# Code (tools/) flach nach /opt/rushmore/
rsync -avz --progress \
  --exclude '__pycache__' --exclude '*.pyc' \
  -e "ssh -i ~/.ssh/id_ed25519" \
  tools/ \
  root@178.104.249.211:/opt/rushmore/

# Assets in /opt/rushmore/assets/ (Unterverzeichnis beibehalten!)
rsync -avz --progress \
  -e "ssh -i ~/.ssh/id_ed25519" \
  assets/ players.json \
  root@178.104.249.211:/opt/rushmore/assets/
```

> Dauert wegen der 87MB Headshots 1-2 Minuten. Bei späteren Deploys überträgt rsync nur Änderungen.

> **Wichtig:** Code sucht Assets über `Path(__file__).parent.parent / "assets"` = `/opt/assets/`.
> Daher Symlink nötig (einmalig): `ln -sfn /opt/rushmore/assets /opt/assets`

---

## Schritt 3 — Dependencies installieren

```bash
ssh -i ~/.ssh/id_ed25519 root@178.104.249.211 \
  "/opt/rushmore/venv/bin/pip install -q fastapi 'uvicorn[standard]' pillow python-dotenv nba-api pydantic requests google-genai"
```

---

## Schritt 4 — Service-User anlegen und systemd-Service einrichten

```bash
# Dedicated unprivileged service user
ssh -i ~/.ssh/id_ed25519 root@178.104.249.211 "
  useradd --system --no-create-home --shell /sbin/nologin rushmore
  chown -R rushmore:rushmore /opt/rushmore
"
```

```bash
ssh -i ~/.ssh/id_ed25519 root@178.104.249.211 "cat > /etc/systemd/system/rushmore-backend.service << 'EOF'
[Unit]
Description=Rushmore FastAPI Backend
After=network.target

[Service]
Type=simple
User=rushmore
Group=rushmore
WorkingDirectory=/opt/rushmore
ExecStart=/opt/rushmore/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8080
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable rushmore-backend
systemctl start rushmore-backend
systemctl status rushmore-backend"
```

---

## Schritt 5 — Testen

```bash
curl http://178.104.249.211:8080/api/categories
```

Antwort sollte JSON mit den Kategorie-Definitionen liefern.

---

## Schritt 6 — Frontend umstellen

In `web/next.config.ts` die Railway-URL ersetzen:

```ts
// vorher:
destination: `https://rushmore-production.up.railway.app/api/:path*`,

// nachher:
destination: `http://178.104.249.211:8080/api/:path*`,
```

Frontend-Deployment triggern (Vercel: einfach pushen).

---

## Schritt 7 — Verify

Website aufrufen, Player-Suche + Card-Generierung testen.  
Danach Railway-Service deaktivieren.

---

## Spätere Deploys (nach Code-Änderungen)

```bash
rsync -avz --progress \
  --exclude '__pycache__' --exclude '*.pyc' \
  -e "ssh -i ~/.ssh/id_ed25519" \
  tools/ \
  root@178.104.249.211:/opt/rushmore/

ssh -i ~/.ssh/id_ed25519 root@178.104.249.211 "chown -R rushmore:rushmore /opt/rushmore && systemctl restart rushmore-backend"
```

---

## Security Hardening (einmalig auf Live-Server ausführen)

Diese Befehle müssen auf dem bereits laufenden Server nachträglich ausgeführt werden:

```bash
ssh -i ~/.ssh/id_ed25519 root@178.104.249.211 "

# 1. Service-User anlegen (falls noch nicht geschehen)
id rushmore 2>/dev/null || useradd --system --no-create-home --shell /sbin/nologin rushmore

# 2. Ownership setzen
chown -R rushmore:rushmore /opt/rushmore

# 3. systemd-Unit auf non-root User umstellen
sed -i 's/^User=root/User=rushmore/' /etc/systemd/system/rushmore-backend.service
sed -i '/^User=rushmore/a Group=rushmore' /etc/systemd/system/rushmore-backend.service

# 4. Service neu starten
systemctl daemon-reload
systemctl restart rushmore-backend
systemctl status rushmore-backend

# 5. Prüfen: Prozess läuft nicht mehr als root
ps aux | grep uvicorn
"
```

```bash
# 6. INTERNAL_API_KEY in VPS .env eintragen
ssh -i ~/.ssh/id_ed25519 root@178.104.249.211 \
  "echo 'INTERNAL_API_KEY=$(openssl rand -hex 32)' >> /opt/rushmore/.env && cat /opt/rushmore/.env | grep INTERNAL_API_KEY"
```

Anschließend den angezeigten Key als `INTERNAL_API_KEY` in Vercel Environment Variables (Settings → Environment Variables) eintragen.
Dann Vercel Deployment neu triggern (git push).

Assets und players.json nur neu deployen wenn sie sich geändert haben.

---

## Logs & Service-Management

```bash
# Status
ssh -i ~/.ssh/id_ed25519 root@178.104.249.211 "systemctl status rushmore-backend"

# Live-Logs
ssh -i ~/.ssh/id_ed25519 root@178.104.249.211 "journalctl -u rushmore-backend -f"

# Restart
ssh -i ~/.ssh/id_ed25519 root@178.104.249.211 "systemctl restart rushmore-backend"
```
