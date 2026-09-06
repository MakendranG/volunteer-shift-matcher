# Deploy the visual demo to Streamlit Community Cloud (free, public URL)

This gives you the **public live demo link** the hackathon rewards (higher
Technical Implementation score) — without needing AgentCore. GitHub Pages will
**not** work here, because Streamlit runs a live Python server (GitHub Pages only
serves static files).

## Which mode runs in the cloud?

- **Offline mode** works out of the box on Streamlit Cloud with zero secrets —
  perfect for a public demo anyone can click.
- **Live agent mode** (Strands + Amazon Bedrock) also works *if* you add AWS
  credentials as Streamlit **secrets** (below). Only do this with a tightly
  scoped, Bedrock-only IAM user — never commit keys.

## Steps

1. Make sure this repo is pushed to GitHub (it is:
   https://github.com/MakendranG/volunteer-shift-matcher).

2. Go to https://share.streamlit.io and sign in with GitHub.

3. Click **Create app** → **Deploy a public app from GitHub** and choose:
   - Repository: `MakendranG/volunteer-shift-matcher`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

4. Click **Deploy**. Streamlit installs `requirements.txt` automatically. In a
   minute you'll get a public URL like
   `https://volunteer-shift-matcher-xxxx.streamlit.app`.

5. (Optional) To enable **Live agent mode** in the cloud, open the app's
   **Settings → Secrets** and add:
   ```toml
   AWS_ACCESS_KEY_ID = "..."
   AWS_SECRET_ACCESS_KEY = "..."
   AWS_REGION = "us-west-2"
   # or, if you use a Bedrock bearer token instead:
   # AWS_BEARER_TOKEN_BEDROCK = "..."
   ```
   Streamlit exposes these as environment variables, which `build_agent()` reads.
   Use an IAM user restricted to `bedrock:InvokeModel*` only.

6. Put the public URL in:
   - the Devpost submission form (as the live demo link),
   - `SUBMISSION.md` → "links to fill in",
   - the app sidebar / README if you like.

## Notes

- Keep offline mode as the safe default for the public link so it always works
  even if Bedrock throttles or credits run out.
- The same app runs locally with `streamlit run streamlit_app.py`.
