# Auto_Translate

An ultra-lightweight **Vietnamese-to-Any-Language** neural machine translator running strictly **beneath 512 MB RAM**.

Powered by **CTranslate2 INT8** and **SentencePiece** (pure C++ engine, zero PyTorch overhead).

---

## 🌐 Live API Deployment

* **Live Base URL:** `https://translation-temporary.onrender.com`
* **Interactive Swagger UI:** [https://translation-temporary.onrender.com/docs](https://translation-temporary.onrender.com/docs)
* **Status:** 🟢 **Online & Public (Zero Setup / No API Key Required)**
* **Full Integration Guide:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## Quick Example: Call the Live API Right Now

### Via cURL (Terminal):
```bash
curl -X POST "https://translation-temporary.onrender.com/translate" \
     -H "Content-Type: application/json; charset=utf-8" \
     -d '{"text": "Xin chào thế giới!", "target": "English"}'
```

### Via JavaScript (Browser / Node.js):
```javascript
const res = await fetch("https://translation-temporary.onrender.com/translate", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ text: "Hôm nay thời tiết rất đẹp.", target: "French" })
});
const data = await res.json();
console.log(data.translated_text);
```

### Via Python:
```python
import requests

res = requests.post(
    "https://translation-temporary.onrender.com/translate",
    json={"text": "Trí tuệ nhân tạo đang thay đổi thế giới.", "target": "Japanese"}
)
print(res.json()["translated_text"])
```

---

## Performance & Memory Benchmarks

* **Base Process RAM:** ~41.1 MB
* **RAM with VI $\to$ EN model loaded:** ~134.9 MB
* **RAM during VI $\to$ FR Pivot translation (2 models simultaneously):** ~229.5 MB
* **Max Peak RAM (with automatic model eviction):** ~234.8 MB (< 512 MB Limit)
* **Execution Latency:** ~10–25 ms per sentence on CPU
* **Memory Drift across requests:** +0.3 MB (Zero memory leak)

---

## REST API Deployment on Render

This service is ready to deploy on **Render.com's Free Web Service tier (512 MB RAM limit)** with zero configuration headaches.

### How to Deploy to Render (Step-by-Step):

1. **Push your code to GitHub / GitLab:**

2. **Create Web Service on Render:**
   * Go to [dashboard.render.com](https://dashboard.render.com) $\rightarrow$ Click **New +** $\rightarrow$ **Web Service**.
   * Connect your GitHub / GitLab repository.
   * Render will auto-detect settings, or configure:
     * **Environment:** `Python`
     * **Region:** `Singapore` (or closest to you)
     * **Branch:** `main`
     * **Build Command:** `pip install -r requirements.txt`
     * **Start Command:** `uvicorn src.auto_translate.api:app --host 0.0.0.0 --port $PORT`
     * **Plan Instance:** `Free` (512 MB RAM)

3. **Configure Environment Variables on Render:**
   In the Render dashboard under **Environment**:
   * `OMP_NUM_THREADS` = `2`
   * `BEAM_SIZE` = `4` (or `1` for extra fast translations)
   * `COMPUTE_TYPE` = `int8`
   * `MAX_CONCURRENCY` = `20`
   * `MAX_ALLOWED_RAM_MB` = `512.0`

4. **Click "Create Web Service"**:
   Render will deploy the service and assign you a public URL (e.g., `https://auto-translate-api.onrender.com`).

---

## API Endpoints & How Others Call It

Once deployed, anyone on the internet can call your API:

### 1. Translate Endpoint (`POST /translate`)

#### Via cURL (Terminal / Bash / PowerShell):
```bash
curl -X POST "https://your-service-name.onrender.com/translate" \
     -H "Content-Type: application/json" \
     -d '{"text": "Xin chào, tôi là lập trình viên.", "target": "English"}'
```

#### JSON Response:
```json
{
  "original_text": "Xin chào, tôi là lập trình viên.",
  "translated_text": "Hello, I am a programmer.",
  "target_language": "English",
  "latency_ms": 78.5,
  "current_ram_mb": 147.9,
  "ram_limit_mb": 512.0
}
```

#### Via JavaScript / Web Frontend (`fetch`):
```javascript
const response = await fetch("https://your-service-name.onrender.com/translate", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    text: "Hôm nay thời tiết rất đẹp.",
    target: "French"
  })
});
const data = await response.json();
console.log(data.translated_text); // "C'est une belle journée."
```

#### Via Python (`requests`):
```python
import requests

res = requests.post(
    "https://your-service-name.onrender.com/translate",
    json={"text": "Chúc một ngày tốt lành.", "target": "Spanish"}
)
print(res.json()["translated_text"]) # "Que tengas un buen día."
```

### 2. Supported Languages Endpoint (`GET /languages`)
```bash
curl "https://your-service-name.onrender.com/languages"
```

### 3. Health & RAM Telemetry Endpoint (`GET /health`)
```bash
curl "https://your-service-name.onrender.com/health"
```

### 4. Interactive Swagger Documentation
Navigate to `https://your-service-name.onrender.com/docs` in your browser to view the interactive OpenAPI UI.

---

## Local Development & Testing

```bash
# Run local API server on http://localhost:8000
python -m src.auto_translate.api

# Run test suite
python run_tests.py
```
