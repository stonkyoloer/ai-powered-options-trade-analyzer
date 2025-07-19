# Overview
Stonk‑Yoloer is an AI‑powered options‑trading pipeline that:Screens for the most liquid, high-IV tickers and builds a basket of the top 6.    

#  Scope
1. Scrape Bartchart.com AIP to build a stock screener 

## How-to Build a Stock Screener

### 🕵️‍♂️ Verify Python 3 and Create a Folder 
Confirm we have a proper Python 3 interpreter (needed for virtual environment) and have a clean workspace directory before proceeding.

#### Step 1: Verify Python 3 [TERMINAL]

````bash
python3 --version
````

#### Step 2: Create the folder [TERMINAL]
````bash
mkdir screener
````

#### Step 3: Move into the folder [TERMINAL]

````bash
cd screener
````

#### Step 4: Confirm you are inside the folder [TERMINAL]

````bash
pwd
````

### 🧱 Create and Activate a Virtual Environment 
Isolate project packages (so versions of pandas, etc. don’t clash with system-wide installs).

#### Step 1: Create the virtual environment [TERMINAL]

````bash
python3 -m venv .venv
````

#### Step 2: Activate the virtual environment [TERMINAL]

````bash
source .venv/bin/activate
````

#### Step 3: Confirm the active python is inside (.vene) [TERMINAL]

````bash
which python
````

#### Step 4: Show python version [TERMINAL]

````bash
python --version
````

### 🤖 Install Required Packages 
pandas = data table handling.
requests = calling the Barchart API.
Upgrading pip first avoids annoying install warnings.

#### Step 1: Upgrade pip [TERMINAL]

````bash
pip install --upgrade pip
````

#### Step 2: Install libraries [TERMINAL]

````bash
pip install pandas requests
````

#### Step 3: Verify they are installed [TERMINAL]

````bash
pip show pandas
````

### 📂 Create config.py 
Central place to hold the API key + base URL so other scripts can import the key; avoids hard‑coding it multiple times.

#### Step 1: Create a new file [Visual Stduio]

````bash
config.py
````

#### Step 2: API Key Place Holder [Visual Studio]

````bash
API_KEY = "PUT_YOUR_KEY_HERE"
BASE_URL = "https://marketdata.websol.barchart.com"
````

#### Step 3: Save the file [Visual Studio]

````bash
ctrl + S
````

#### Step 4: Create a file in terminal [TERMINAL]

````bash
cat > config.py <<'EOF'
API_KEY = "PUT_YOUR_KEY_HERE"
BASE_URL = "https://marketdata.websol.barchart.com"
EOF
````

#### Step 5: Verify a file exists in terminal [TERMINAL]

````bash
ls -l config.py
````

#### Step 6: Show contents within file [TERMINAL]

````bash
cat config.py
````

### 🏃‍♂️ Create a test_run.py 
To verify: (a) file imports work, (b) we can execute within the venv, (c) path is correct.


#### Step 1:  Create a new file [terminal]

````bash
cat > test_run.py <<'EOF'
import config

print("Config loaded. Base URL =", config.BASE_URL)
print("API key placeholder length =", len(config.API_KEY))
EOF
````

#### Step 2: Verify the file exists [terminal]

````bash
ls -l test_run.py
````

### 🧑‍💻 Create fetch_leaders.py
Creating a script that will (soon) fetch option volume leaders from Barchart. For now it just sets up the request function and prints a URL (no actual API call yet because key is placeholder).

#### Step 1: Create the file [terminal]

````bash
cat > fetch_leaders.py <<'EOF'
import requests
import config

def api_get(endpoint, params=None):
    """
    Basic GET wrapper.
    endpoint: path after base, e.g. '/getOptionVolumeLeaders.json'
    params: dict of query params (apikey added automatically)
    """
    if params is None:
        params = {}
    params['apikey'] = config.API_KEY
    url = config.BASE_URL + endpoint
    print("DEBUG requesting:", url)
    resp = requests.get(url, params=params, timeout=10)
    print("HTTP status:", resp.status_code)
    if resp.status_code == 200:
        try:
            js = resp.json()
            print("Top-level keys:", list(js.keys()))
            if 'results' in js and isinstance(js['results'], list):
                print("Number of results:", len(js['results']))
        except Exception as e:
            print("JSON parse error:", e)
    else:
        print("Response text (truncated):", resp.text[:200])

if __name__ == "__main__":
    api_get("/getOptionVolumeLeaders.json", params={"limit": 5})
EOF
````

#### Step 2: Confirm the file exists 

````bash
ls -l fetch_leaders.py
````

#### Step 3: Run the script

````bash
python fetch_leaders.py
````



