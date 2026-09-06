# Optional: Deploy to Amazon Bedrock AgentCore

> **Optional, not required.** The hackathon rules state deploying with AgentCore
> is "a smart architectural choice and will strengthen your Technical
> Implementation score, but it's not required." This note gives you a clean path
> if you want that boost. The core project runs fine locally without it.

AgentCore Runtime lets you host your Strands agent as a managed HTTP service so
you can offer a **live demo link** (which also scores higher).

## The idea

Wrap the existing `shift_matcher_agent` in an AgentCore entrypoint. You do **not**
rewrite the agent — you reuse `shift_matcher.agent.build_agent()` and expose it.

## Steps (high level)

1. Install the toolkit and runtime SDK:
   ```bash
   pip install bedrock-agentcore-starter-toolkit bedrock-agentcore
   ```

2. Create an entrypoint file, e.g. `agentcore_app.py`:
   ```python
   """AgentCore Runtime entrypoint for the Volunteer Shift Matcher.

   Reuses the same Strands agent used by the CLI — no logic is duplicated.
   Credentials are read from the environment / IAM role (no hardcoded keys).
   """
   import json
   from bedrock_agentcore.runtime import BedrockAgentCoreApp
   from shift_matcher.agent import build_agent

   app = BedrockAgentCoreApp()
   agent = build_agent(callback_handler=None)

   @app.entrypoint
   def invoke(payload):
       # payload is expected to contain {"shifts": [...], "volunteers": [...]}
       shifts = payload.get("shifts", [])
       volunteers = payload.get("volunteers", [])
       prompt = (
           "Call the match_shifts tool, then draft the confirmation and "
           "help-needed messages, and reply with the JSON object described in "
           "your instructions.\n\n"
           f"OPEN SHIFTS:\n{json.dumps(shifts)}\n\nVOLUNTEERS:\n{json.dumps(volunteers)}"
       )
       result = agent(prompt)
       return {"result": str(getattr(result, "message", result))}

   if __name__ == "__main__":
       app.run()
   ```

3. Configure and deploy with the starter toolkit CLI:
   ```bash
   agentcore configure --entrypoint agentcore_app.py
   agentcore launch
   ```

4. Invoke the deployed runtime to confirm, then use its endpoint as your
   **live demo link** in the Devpost submission.

## Notes

- Follow the official guide for exact CLI flags and IAM setup:
  https://strandsagents.com/docs/user-guide/deploy/deploy_to_bedrock_agentcore/python/
  and https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-toolkit.html
- Verify the deploy end-to-end before you record/submit — the rules warn that AI
  tools can hallucinate APIs, so test what you plan to show.
- Keep the local CLI (`run_agent.py`) as your reliable demo path; AgentCore is
  the bonus.
