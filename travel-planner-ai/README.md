# Travel Planner AI (Flask + IBM Watsonx.ai Granite)

A simple Flask app that sends your trip details to a deployed Granite LLM on IBM Watsonx.ai and returns a structured plan.

## Setup

1. Python 3.9+ recommended.
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in your values:

```
WATSONX_API_KEY=your_api_key
WATSONX_DEPLOYMENT_URL=https://us-south.ml.cloud.ibm.com/ml/v4/deployments/<deployment_id>/ai_service?version=2021-05-01
```

- Use `ai_service_stream` in the URL if your deployment is streaming, otherwise use `ai_service`.

## Run

```powershell
python app.py
```

Open http://127.0.0.1:5000/ in your browser.

## Notes
- The app gets an IAM token using your API key, then calls the deployment URL with the Granite chat payload.
- If you get HTTP errors, the UI will show details including status code and response body to help debug.
