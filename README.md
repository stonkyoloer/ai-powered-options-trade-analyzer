# Overview

Stonk‑Yoloer is running an AI‑powered options‑trading pipeline that uses python to request api access from tastytrade, a stock trading brokerage designed for developers to build trading algorithms.



#  Scope

1. Open a tastytrade account, enable API access, gather data.
2. Screen data.
3. Select 6 stock tickers for trading

### Build Stock Screener

#### 1.  Create a base project folder structure

Set up the base folders (config/, src/stonk_yoloer/, data/raw/, tests/) so the project isn’t a landfill. This keeps later files landing in predictable spots.  [terminal]

````bash
mkdir -p stonk_yoloer/{config,src/stonk_yoloer,data/raw,tests} \
&& cd stonk_yoloer \
&& pwd \
&& ls -1
````

#### 2. Create config/settings.py 

Centralizes all API keys & tunable parameters in one place; every component (tastytrade, polygon, etc.) imports this instead of duplicating config logic. [terminal]

````bash
cat > config/settings.py <<'EOF'
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # Tastytrade (we will populate .env later)
    tasty_base_url: str = Field("https://api.tastytrade.com", env="TASTY_BASE_URL")
    tasty_username: str = Field("", env="TASTY_USERNAME")  # keep empty for now
    tasty_password: str = Field("", env="TASTY_PASSWORD")

    request_timeout: float = Field(5.0, env="REQUEST_TIMEOUT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
EOF
````

Verify file contents 

````bash
sed -n '1,160p' config/settings.py
````

#### 3. Initialize a Python virtual environment for isolated dependencies

Keeps project packages separate from system Python; ensures reproducibility and prevents version conflicts. [terminal]

````bash
python3 -m venv .venv && source .venv/bin/activate && python -V
````

#### 4. Install the minimal dependency set

Required to make the forthcoming Tastytrade client work; installs libraries inside the virtual environment. [terminal]


````bash
pip install --upgrade pip && pip install httpx pydantic python-dotenv
````

verify key packages 

````bash
pip show httpx | grep Version
pip show pydantic | grep Version
````

#### 5. Create a .env file with Tastytrade credentials

Your Settings class will read these values; keeping them in .env separates secrets from code and prevents accidental commits. [terminal]

````bash
# Create .env with placeholders (edit later with real creds)
cat > .env <<'EOF'
TASTY_USERNAME=PUT_USERNAME_HERE
TASTY_PASSWORD=PUT_PASSWORD_HERE
# Optional override:
# TASTY_BASE_URL=https://api.tastytrade.com
EOF

# Create or append to .gitignore to exclude secrets & venv
grep -q "^.env$" .gitignore 2>/dev/null || {
  printf ".env\n.venv/\n__pycache__/\n*.pyc\n" >> .gitignore
}

# Show the .env so you can confirm contents
sed -n '1,120p' .env
````

#### 6. Create a minimal Tastytrade client file with just login

To verify credentials + session token before adding more complexity. If login works, downstream calls will be simpler to debug. [terminal]

````bash
cat > src/stonk_yoloer/tasty_client.py <<'EOF'
import httpx
from config.settings import settings

def login():
    if not settings.tasty_username or not settings.tasty_password:
        raise SystemExit("Username/password empty. Edit .env first.")
    url = f"{settings.tasty_base_url.rstrip('/')}/sessions"
    payload = {"login": settings.tasty_username, "password": settings.tasty_password}
    with httpx.Client(timeout=settings.request_timeout) as c:
        r = c.post(url, json=payload)
        try:
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            print("Status error:", e.response.status_code, e.response.text[:200])
            raise
    data = r.json()
    token = (
        data.get("data", {}).get("session-token")
        or data.get("data", {}).get("sessionToken")
        or data.get("session-token")
    )
    if not token:
        print("Raw response (truncated):", str(data)[:300])
        raise SystemExit("No session token found in response.")
    print("Logged in. Token length:", len(token))
    return token

if __name__ == "__main__":
    login()
EOF
````

Run:

````bash
python src/stonk_yoloer/tasty_client.py
````

#### 7. Fix import error 

Python couldn’t find config (ModuleNotFoundError) because the interpreter didn’t treat the config/ directory as a package on your sys.path. Adding __init__.py (and confirming you’re in the project root) resolves that reliably. [terminal]

````bash
# Ensure we are in project root
pwd

# Create __init__.py so 'config' is a proper package
touch config/__init__.py

# (Optional) show structure to sanity-check
ls -1 config

# Re-run the client
python src/stonk_yoloer/tasty_client.py
````

#### 7. (Revised Fix) Re-run the login script with PYTHONPATH

To make the config package discoverable and eliminate the ModuleNotFoundError. [terminal]

````bash
PYTHONPATH=. python src/stonk_yoloer/tasty_client.py
````

#### 8. Fix the Pydantic v2 import error by installing pydantic-settings and updating settings.py to import BaseSettings from the correct package.

In Pydantic v2, BaseSettings moved out of pydantic into pydantic_settings; current import causes the crash you saw. [terminal]

````bash
# 1. Install the new package
pip install pydantic-settings

# 2. Replace the first import line in settings.py
# (Backup optional)
cp config/settings.py config/settings.py.bak

# Update the import line to use pydantic_settings
sed -i '' '1s/^from pydantic import BaseSettings, Field$/from pydantic_settings import BaseSettings\nfrom pydantic import Field/' config/settings.py

# 3. Show the updated top lines to verify
sed -n '1,20p' config/settings.py

# 4. Re-run the client (with project root on PYTHONPATH)
PYTHONPATH=. python src/stonk_yoloer/tasty_client.py
````

#### 9. Enter tastytrade login credientials

Putting your Tastytrade login (username + password) into the .env file, then running the login script to get a session token.  he script reads .env to authenticate [terminal]

````bash
nano .env
````

Inside the editor, change the two lines to  your login creds):

````bash
TASTY_USERNAME= STONKYOLOER
TASTY_PASSWORD= PASSWORD_1
````

press ctrl + O (save)
press ctrl + X (quit)

Then run the login script

````bash
PYTHONPATH=. python src/stonk_yoloer/tasty_client.py
````

#### 10.Add a function to fetch a single option chain

A saved raw chain file is the foundation for building your screener and later parsing metrics (IV rank, spreads, volume). [terminal]

````bash
nano src/stonk_yoloer/tasty_client.py
````

Inside the editor replace the whole file contents with

````bash
import httpx, json, time, pathlib
from config.settings import settings

RAW_DIR = pathlib.Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def login():
    if not settings.tasty_username or not settings.tasty_password:
        raise SystemExit("Username/password empty. Edit .env first.")
    url = f"{settings.tasty_base_url.rstrip('/')}/sessions"
    payload = {"login": settings.tasty_username, "password": settings.tasty_password}
    with httpx.Client(timeout=settings.request_timeout) as c:
        r = c.post(url, json=payload)
        r.raise_for_status()
    data = r.json()
    token = (
        data.get("data", {}).get("session-token")
        or data.get("data", {}).get("sessionToken")
        or data.get("session-token")
    )
    if not token:
        raise SystemExit("No session token found.")
    return token

def get_option_chain(token: str, symbol: str):
    url = f"{settings.tasty_base_url.rstrip('/')}/option-chains/{symbol.upper()}"
    headers = {"Authorization": token}
    with httpx.Client(timeout=10.0, headers=headers) as c:
        r = c.get(url)
        r.raise_for_status()
    return r.json()

def save_raw(prefix: str, symbol: str, data: dict):
    ts = int(time.time())
    path = RAW_DIR / f"tasty_{prefix}_{symbol}_{ts}.json"
    path.write_text(json.dumps(data, indent=2))
    return path

if __name__ == "__main__":
    token = login()
    print("Logged in. Token length:", len(token))
    symbol = "NVDA"
    chain = get_option_chain(token, symbol)
    out_path = save_raw("chain", symbol, chain)
    items = chain.get("data", {}).get("items") or []
    print(f"Saved chain to {out_path} with {len(items)} items")
````

Save it: Ctrl + O (enter)
Close it:Ctrl + X (enter)

Then run: 

````bash
PYTHONPATH=. python src/stonk_yoloer/tasty_client.py
````

#### 10. 


