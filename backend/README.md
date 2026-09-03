# Cyclone Shakti AI — Backend

AI-powered tropical cyclone platform for India: detection, intensity prediction,
trajectory forecasting, GeoJSON visualization, multilingual advisories, alerting
and analytics. Designed for Smart India Hackathon (SIH) and ready for future
real-time data and real ML/CV model integration.

---

## 1. Project overview

Cyclone Shakti AI Backend is a **FastAPI + SQLAlchemy** service exposing a
RESTful + optional WebSocket API for:

- Cyclone **detection** from location / future satellite imagery inputs.
- **Intensity prediction** (wind speed + category classification).
- **Track / trajectory forecasting** with automatic GeoJSON LineString output.
- **Multilingual advisories** (English, Hindi, extensible).
- **Configurable alert evaluation** (LOW / MODERATE / HIGH / EXTREME).
- **Analytics** summary + per-cyclone historical observations & predictions.
- A **frontend-compatible `/cyclone/current`** payload that the React dashboard
  already consumes.

Key design principles:

1. **Real, production-grade interfaces — mock inference today.** Routes and
   services never fake AI: they delegate to a clean `BaseModel.load() / predict()`
   interface so your ML teammate can replace the `Mock*Model` implementations
   with real PyTorch / TensorFlow / Scikit-learn / ONNX models *without
   touching any API route*.
2. **Never crash when a real model is missing.** If `models/` is empty, the app
   logs a warning and falls back to deterministic mock implementations.
3. **DB-persist where useful, demo where DB is empty.** Observations, predictions,
   forecast points and alerts are saved to SQLite (dev) / PostgreSQL (prod); if
   the database has no rows, analytics transparently return labeled `mock_demo`
   data so dashboards are never blank.
4. **No fake scientific claims.** Intensity thresholds and alert rules live in
   `app/core/config.py` with explicit comments so they can be updated per the
   final official standard the project selects.

---

## 2. Architecture

```
┌─────────────┐      ┌─────────────────────┐      ┌────────────────────┐
│  HTTP API   │──────▶   app/api/routes/*   │──────▶  app/services/*    │
│ (FastAPI)   │      │  (routing + Depends) │      │ (business logic)   │
└─────────────┘      └─────────────────────┘      └───────┬────────────┘
                                                          │
                             ┌────────────────────────────┼──────────┐
                             ▼                            ▼          ▼
                     ┌──────────────┐           ┌────────────┐  ┌──────────────┐
                     │ app/ml/*     │           │ app/data/* │  │ app/database │
                     │ models +     │           │ loading /  │  │ repository + │
                     │ loader       │           │ clean +    │  │ connection   │
                     └──────────────┘           │ preprocess │  └──────────────┘
                                                └────────────┘
```

- **Routes** are thin: they validate (via Pydantic) and delegate to services.
- **Services** orchestrate models + storage.
- **ML layer** loads models once on startup, validates input, predicts.
- **DB layer** is isolated behind `CycloneRepository` (SQLAlchemy).

---

## 3. Folder structure

```
backend/
├── app/
│   ├── main.py                      # FastAPI app, lifespan, CORS, WS, error handlers
│   ├── api/
│   │   └── routes/
│   │       ├── health.py            # GET / , GET /health
│   │       ├── cyclone.py           # GET /cyclone/current
│   │       ├── prediction.py        # POST /predict-{detection,intensity,track}
│   │       ├── advisory.py          # POST /generate-alert + GET languages
│   │       ├── alerts.py            # POST /alerts/evaluate
│   │       └── analytics.py         # GET /analytics/{summary, cyclone/:id}
│   ├── core/
│   │   ├── config.py                # Settings, thresholds, alert rules, CORS
│   │   ├── logging_config.py        # Console + rotating file loggers
│   │   └── exceptions.py            # AppError hierarchy + typed error codes
│   ├── models/
│   │   ├── schemas.py               # Pydantic request / response schemas
│   │   └── database_models.py       # SQLAlchemy ORM models (Cyclone, Observation, …)
│   ├── services/
│   │   ├── cyclone_service.py       # Builds /cyclone/current (DB then mock)
│   │   ├── detection_service.py     # Detection inference + persist
│   │   ├── intensity_service.py     # Intensity inference + persist
│   │   ├── trajectory_service.py    # Track inference + GeoJSON + persist
│   │   ├── advisory_service.py      # Multilingual advisory templating
│   │   ├── alert_service.py         # Configurable severity engine
│   │   └── analytics_service.py     # Aggregation + demo fallback
│   ├── ml/
│   │   ├── base_model.py            # BaseModel ABC (load/validate_input/predict)
│   │   ├── model_loader.py          # Startup loader, framework auto-detect
│   │   ├── detection_model.py       # DetectionModel + MockDetectionModel
│   │   ├── intensity_model.py       # IntensityModel + MockIntensityModel
│   │   └── trajectory_model.py      # TrajectoryModel + MockTrajectoryModel
│   ├── data/
│   │   ├── data_loader.py           # Extensible data source loader
│   │   ├── preprocessing.py         # Clean + normalize + feature vector
│   │   └── mock_data.py             # Curated demo current + historical
│   ├── database/
│   │   ├── connection.py            # SQLAlchemy engine + session + lifespan
│   │   └── repository.py            # CycloneRepository: all CRUD in one place
│   └── utils/
│       ├── geojson.py               # validate_coordinates + forecast_points_to_geojson
│       ├── validation.py            # classify_intensity + severity mappers
│       └── helpers.py               # IDs, distances, clamping, rounding
├── tests/
│   ├── test_health.py               # root, health, current, validation errors
│   ├── test_cyclone.py              # predict-{detection,intensity,track}
│   ├── test_prediction.py           # classify_intensity, GeoJSON, analytics
│   └── test_advisory.py             # advisories EN/HI + alerts evaluate
├── models/
│   └── .gitkeep                     # Drop trained models here
├── data/
│   └── sample/.gitkeep              # Drop sample satellite/weather files here
├── requirements.txt
├── .env.example
├── .gitignore
├── run.py                           # Alternative entry (same as uvicorn …)
└── README.md
```

---

## 4. Installation

### 4.1 Virtual environment

```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4.2 Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.3 Environment variables

Copy the template and edit for your local machine:

```bash
cp .env.example .env
```

```dotenv
APP_ENV=development
DATABASE_URL=sqlite:///./cyclone.db
FRONTEND_URL=http://localhost:5173
OPENAI_API_KEY=
GEMINI_API_KEY=
LOG_LEVEL=INFO
```

Secrets are **never** hard-coded. Optional LLM advisory integration reads
keys from the environment only.

---

## 5. Run the backend

### Dev server (auto-reload)

```bash
uvicorn app.main:app --reload
```

Or via `run.py`:

```bash
python run.py
```

### Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 6. Swagger / ReDoc / OpenAPI

- Swagger UI:  [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc:      [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- OpenAPI:    [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

You can try every endpoint directly from the Swagger UI — it includes
`Try it out` buttons and auto-generated example bodies.

---

## 7. All available API endpoints

### 7.1 Root / health

| Method | Path       | Description                                      |
|--------|------------|--------------------------------------------------|
| GET    | `/`        | Welcome message (frontend “is backend up?” ping) |
| GET    | `/health`  | Service name, version, DB availability flag.     |

### 7.2 Cyclone

| Method | Path               | Description                                                                          |
|--------|--------------------|--------------------------------------------------------------------------------------|
| GET    | `/cyclone/current` | Frontend-compatible payload. Materializes from DB, else falls back to curated demo.  |

### 7.3 Prediction

| Method | Path                   | Input shape                                                                 |
|--------|------------------------|-----------------------------------------------------------------------------|
| POST   | `/predict-detection`   | `{ image_path?, latitude?, longitude?, timestamp?, metadata? }`            |
| POST   | `/predict-intensity`   | `{ cyclone_id, latitude, longitude, current_wind_speed, pressure?, temp?, humidity?, timestamp? }` |
| POST   | `/predict-track`       | `{ cyclone_id, current_position:{lat,lon}, current_wind_speed, forecast_hours: 6..240 }` |

### 7.4 Advisory

| Method | Path                   | Description                                                                 |
|--------|------------------------|-----------------------------------------------------------------------------|
| POST   | `/generate-alert`      | Builds advisory with severity-ranked `recommended_actions`. EN / HI today. |
| GET    | `/advisory/languages`  | Lists supported advisory languages.                                        |

### 7.5 Alerts

| Method | Path                | Description                                                      |
|--------|---------------------|------------------------------------------------------------------|
| POST   | `/alerts/evaluate`  | Evaluates severity from wind-speed + category + confidence.     |

### 7.6 Analytics

| Method | Path                          | Description                                                                        |
|--------|-------------------------------|------------------------------------------------------------------------------------|
| GET    | `/analytics/summary`          | Totals + averages.                                                                  |
| GET    | `/analytics/cyclone/{id}`     | Full history (observations + predictions) tagged `data_source: database \| mock_demo`. |

### 7.7 WebSocket

| URL                            | Behaviour                                                                  |
|--------------------------------|----------------------------------------------------------------------------|
| `ws://127.0.0.1:8000/ws/cyclone/{cyclone_id}` | Sends lightweight mock `position_update` frames every 5 seconds. Designed for future real-time feed integration. |

---

## 8. Example requests / responses

### 8.1 `GET /cyclone/current`

```jsonc
{
  "cyclone_id": "CY001",
  "center": { "latitude": 15.52, "longitude": 73.21 },
  "detection_confidence": 0.94,
  "intensity": {
    "predicted_wind_speed": 145.2,
    "intensity_category": "Severe Cyclonic Storm",
    "confidence": 0.87
  },
  "track": {
    "forecast_hours": 48,
    "forecast_points": [
      { "hour": 0,  "latitude": 15.52, "longitude": 73.21, "wind_speed": 120 },
      { "hour": 12, "latitude": 16.2,  "longitude": 73.8,  "wind_speed": 128 },
      { "hour": 24, "latitude": 17.1,  "longitude": 74.5,  "wind_speed": 138 },
      { "hour": 48, "latitude": 18.8,  "longitude": 76.0,  "wind_speed": 145 }
    ],
    "geojson": {
      "type": "LineString",
      "coordinates": [
        [73.21, 15.52],
        [73.8,  16.2 ],
        [74.5,  17.1 ],
        [76.0,  18.8 ]
      ]
    }
  },
  "advisory": {
    "severity": "HIGH",
    "language": "Hindi",
    "message": "Cyclone activity detected. Please follow official disaster management advisories."
  }
}
```

GeoJSON coordinates always use `[longitude, latitude]` order.

### 8.2 `POST /predict-detection`

Request:

```json
{ "latitude": 15.52, "longitude": 73.21, "timestamp": "2026-09-03T12:00:00" }
```

Response:

```json
{
  "cyclone_detected": true,
  "confidence": 0.94,
  "center": { "latitude": 15.52, "longitude": 73.21 },
  "cyclone_id": "CY012-A3F2"
}
```

### 8.3 `POST /predict-intensity`

Request:

```json
{
  "cyclone_id": "CY001",
  "latitude": 15.52,
  "longitude": 73.21,
  "current_wind_speed": 120,
  "pressure": 980,
  "temperature": 28.5,
  "humidity": 80
}
```

Response:

```json
{
  "cyclone_id": "CY001",
  "predicted_wind_speed": 145.2,
  "intensity_category": "Severe Cyclonic Storm",
  "confidence": 0.87
}
```

### 8.4 `POST /predict-track`

Response includes `geojson: LineString([[lon,lat], …])` matching forecast points.

### 8.5 `POST /generate-alert`

`language: English` or `Hindi`. Returns severity + message + `recommended_actions[]`.
Always appends a disclaimer reminding recipients to follow official IMD/NDRF guidance.

### 8.6 `POST /alerts/evaluate`

```json
{
  "alert_triggered": true,
  "severity": "HIGH",
  "reason": "High predicted wind speed",
  "message": "High risk — act on official advisories and be ready to evacuate if ordered.",
  "cyclone_id": "CY001"
}
```

### 8.7 Error format

Consistent JSON shape across all 4xx / 5xx:

```json
{
  "error": "Cyclone with id 'CYNOPE' not found",
  "code": "CYCLONE_NOT_FOUND",
  "details": { "optional": "extra info" }
}
```

Common codes: `VALIDATION_ERROR`, `INVALID_COORDINATES`, `MISSING_FIELDS`,
`CYCLONE_NOT_FOUND`, `UNSUPPORTED_LANGUAGE`, `MODEL_INFERENCE_ERROR`,
`DATABASE_ERROR`, `INTERNAL_ERROR`.

---

## 9. Frontend integration (React)

The frontend runs on `http://localhost:5173` by default. CORS allows this
origin in development via `FRONTEND_URL`; production should pin an explicit
origin list.

### Example React `fetch()` for `/cyclone/current`

```ts
const res = await fetch(`${import.meta.env.VITE_API_URL}/cyclone/current`);
if (!res.ok) throw new Error(`HTTP ${res.status}`);
const data = await res.json();

// fields the React dashboard already expects:
console.log(data.cyclone_id);
console.log(data.center.latitude, data.center.longitude);
console.log(data.detection_confidence);
console.log(data.intensity.predicted_wind_speed,
            data.intensity.intensity_category,
            data.intensity.confidence);
console.log(data.track.forecast_hours);
console.log(data.track.forecast_points);   // array of {hour, lat, lon, ws}
console.log(data.track.geojson);           // Leaflet / mapbox compatible
console.log(data.advisory.severity,
            data.advisory.language,
            data.advisory.message);
```

### Example env (frontend `.env.local`)

```dotenv
VITE_API_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000
```

---

## 10. ML model integration (for your ML teammate)

### 10.1 Model loading contract

1. Drop a trained file into `backend/models/`.
2. Naming hint: the loader auto-picks files whose stem contains one of:
   - `detection`, `detect`, `yolo`, `cv`, `satellite` → DetectionModel
   - `intensity`, `wind`, `regression`                → IntensityModel
   - `trajectory`, `track`, `forecast`, `lstm`, `seq` → TrajectoryModel
3. File extension selects the backend:
   - `.pth` / `.pt`         → PyTorch (`torch.load`)
   - `.h5` / `.pb`          → TensorFlow/Keras (`load_model`)
   - `.pkl` / `.joblib`     → Scikit-learn (`joblib.load`)
   - `.onnx`                → ONNX Runtime
4. Only the framework actually needed must be `pip install`'d.

### 10.2 Code contract

Override in the appropriate `*Model` class:

- `_load_impl(path)` — deserializes into `self._model`.
- `validate_input(input_dict)` — raises `ModelInferenceError` on bad shape.
- `predict(input_dict)` — returns exactly the same dict keys the mock uses today:
  - **Detection** → `{cyclone_detected, confidence, center:{lat,lon}, cyclone_id?}`
  - **Intensity** → `{cyclone_id, predicted_wind_speed, intensity_category, confidence}`
  - **Trajectory** → `{cyclone_id, forecast_hours, forecast_points:[{hour,lat,lon,wind_speed}]}`

That’s the entire contract. **No route or service file needs to change.**

If the real model needs different preprocessing:
- Document features → the team updates `preprocessing.py` helpers accordingly.

---

## 11. Testing

```bash
pytest -q
```

Coverage summary:

| File               | Scenarios tested                                                                 |
|--------------------|----------------------------------------------------------------------------------|
| `test_health.py`   | Root, `/health` status + version, `/cyclone/current` frontend fields, invalid latitude, missing fields 422. |
| `test_cyclone.py`  | `/predict-detection` success & bad coords; `/predict-intensity` success shape; `/predict-track` GeoJSON length match + missing position 422. |
| `test_prediction.py` | `classify_intensity` monotonicity, GeoJSON `[lon, lat]` ordering, `/analytics/summary`, `/analytics/cyclone/CY001` mock. |
| `test_advisory.py` | `/generate-alert` EN, HI, unsupported 400, missing location 422; `/alerts/evaluate` HIGH and LOW cases. |

All tests pass **without** real model files (they rely on the Mock* fallback path).

---

## 12. Git workflow

```bash
# Feature branch
git checkout -b feature/your-feature
# develop, run tests…
pytest -q
git add -A
git commit -m "feat(component): concise description"
git push -u origin feature/your-feature
# Open PR targeting main. Squash merge when CI green.
```

Hygiene:
- Never commit `.env`, `venv/`, `__pycache__/`, database files, or large model
  weights (`.gitignore` already excludes them).
- Run `pytest -q` + confirm `/docs` opens before every merge.

---

## 13. Production / deployment notes

- Database: set `DATABASE_URL=postgresql+psycopg://user:pass@host/cyclone`
  (all SQLAlchemy code is DB-agnostic).
- CORS: set `APP_ENV=production` and `FRONTEND_URL=https://your-frontend.vercel.app`.
- Workers: `uvicorn app.main:app --workers 4` behind a reverse proxy (nginx / Caddy).
- Model files: load once on startup; keep them in a directory backed by disk
  (serverless deployments: mount a volume or bundle with the image).

---

Enjoy building Cyclone Shakti AI 🌀 — routes are stable, and your ML teammate
can plug real models in without API churn.
