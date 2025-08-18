# ✒️ Configure TastyTrade

## 🛠 Create a Project

**Create:** `mkdir tastytrade_data`

**Open:** `cd tastytrade_data`

**Install:** `pip install tastytrade websockets pandas httpx certifi`

  - `tastytrade`: Lets the project talk to the Tastytrade website to get data.
  - `websockets`: Helps get live updates on the Greeks.
  - `pandas`: Handles and calculates with the data.
  - `httpx` and `certifi`: Make secure connections to the internet.


## 🔐 Test Tastytrade Connection


**Create:** `touch test_connection.py`

**Query:** `open -e test_connection.py`

```python
import requests
import json

# Test basic connection to TastyTrade
print("Testing TastyTrade API connection...")

url = "https://api.tastytrade.com/sessions"
print(f"API URL: {url}")
print("Ready for authentication test")
```
**Run:** `python3 test_connection.py`


## 🔑 Authenticate & Get Account Info

**Create:** touch auth_test.py

**Query:** open -e auth_test.py

```python
import requests
import json

# Your TastyTrade credentials
USERNAME = "USERNAME"
PASSWORD = "PASSWORD"

# Test authentication
url = "https://api.tastytrade.com/sessions"
data = {
    "login": USERNAME,
    "password": PASSWORD
}

print("Attempting to authenticate...")
response = requests.post(url, json=data)
print(f"Status code: {response.status_code}")

if response.status_code == 201:
    print("SUCCESS: Authentication worked!")
    result = response.json()
    print("Session token received")
else:
    print("FAILED: Authentication failed")
    print(f"Error: {response.text}")
```

**Run:** `python3 auth_test.py`

## 📂 Configuration

**Create:** `config.py`

**Query:** `open -e config.py`

```bash
# config.py
USERNAME = "YOUR_TASTYTRADE_USERNAME"
PASSWORD = "YOUR_TASTYTRADE_PASSWORD"
```
**Run:** `python 3 config.py`
