# Deploy the visual demo to Streamlit Community Cloud (free, public URL)

This gives you the **public live demo link** the hackathon rewards (higher
Technical Implementation score) — without needing AgentCore. GitHub Pages will
**not** work here, because Streamlit runs a live Python server (GitHub Pages only
serves static files).

## Which mode runs in the cloud?

**This project's public demo is deployed KEYLESS (recommended).** With no AWS
secrets configured, the app auto-detects that and defaults to **Offline mode**,
so:
- the public link always works for any visitor,
- it can never error on missing credentials,
- it can never run up Bedrock charges on your account.

Offline mode still demonstrates the full product: the deterministic matching, gap
detection, colour-coded plan, confirmations, and help-needed broadcasts. Only the
message *wording* is templated instead of LLM-drafted. The full Strands + Amazon
Bedrock agent path is shown in the demo video / `python run_agent.py` locally.

Optional (not used for the public deploy): you *can* enable **Live agent mode** in
the cloud by adding AWS credentials as Streamlit **secrets** (below). Only do this
with a tightly scoped, Bedrock-only IAM user — never commit keys. Note that every
public visitor's click would then spend Bedrock tokens on your account.

## Let visitors test the LIVE agent on THEIR OWN AWS (bring-your-own credentials)

The app includes an optional sidebar panel — **"🔐 Test the LIVE agent with your
own AWS"** — so a judge or visitor can run the real Strands + Bedrock agent using
their **own** AWS account. This is the safe way to offer a live experience without
exposing your keys:

- The visitor pastes **temporary/STS session credentials** (Access Key ID, Secret
  Access Key, **Session Token**, region). Get them via IAM Identity Center / SSO
  "access keys", or `aws sts get-session-token --duration-seconds 3600`.
- Credentials are held **only in that browser session**, used to build a per-request
  boto3 session for the Bedrock call, and are **never stored, logged, or committed**.
  Closing the tab clears them.
- Their Bedrock usage bills to **their** account, not yours.
- Their AWS identity needs `bedrock:InvokeModel` permission and Bedrock model
  access enabled for Claude in the chosen region.

A note on "sign in with AWS console session": a web app cannot read or borrow a
visitor's AWS Console login (browser cross-site cookie isolation + AWS design), so
short-lived STS credentials are the practical, secure equivalent.

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
