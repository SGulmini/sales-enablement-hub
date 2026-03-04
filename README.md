# AI Sales Enablement Hub

Prototype for Digital Customer Experience Manager workflows at FMCG companies.

Live app: https://sales-enablement.streamlit.app/

## How to run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Set `OPENAI_API_KEY` in your environment before running.

## Deploy on Streamlit Community Cloud

1. Push your code to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **"New app"** and select:
   - **Repository**: your-username/sales-enablement-hub
   - **Branch**: main (or master)
   - **Main file path**: app.py
4. Under **"Advanced settings"**, add the secret:
   - `OPENAI_API_KEY` = your OpenAI API key
5. Click **"Deploy"**.
