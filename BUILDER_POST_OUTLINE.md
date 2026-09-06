# Bonus Points: builder.aws.com Build-Story Post

> The rules award **bonus points** for publishing a post on builder.aws.com about
> your build journey and use of AWS. **Your title must contain "Agents for
> Humans"**, and the post must be publicly published before the submission
> deadline. You may submit more than one post.

This is a ready-to-adapt outline. Write it in your own voice — judges reward a
genuine build story, not marketing copy.

## Suggested title options (must include "Agents for Humans")

- "Agents for Humans: Building a Volunteer Shift Matcher with the Strands Agents SDK"
- "How I built an Agents for Humans project to fill a food bank's empty shifts"

## Outline

1. **The hook / the problem (1 short paragraph)**
   Open with the coordinator drowning in a spreadsheet and group texts. Make the
   pain concrete: an unfilled shift = food not sorted, neighbors not served.

2. **Why this track (Good Neighbor Agents)**
   The rules literally name "matching volunteers to the shifts a food bank
   actually needs." Explain why you picked a group-serving problem.

3. **The key design decision: deterministic tool + LLM drafting**
   Explain the split — a Python `@tool` (`match_shifts`) for auditable,
   reproducible assignments, and the LLM only for the warm human messages. This
   is the most interesting technical point; show the `@tool` snippet.

4. **Building with the Strands Agents SDK**
   How little code it took to get a working agent: `from strands import Agent,
   tool`, decorate a function, pass it to `Agent(tools=[...])`. Mention the agent
   loop calling your tool. Link the Strands quickstart.

5. **Using AWS**
   Amazon Bedrock (Claude Sonnet 4) as the model provider; how credentials are
   handled via environment/IAM (no hardcoded keys). If you deployed to AgentCore,
   describe that and share the live endpoint.

6. **The realistic-scenario insight**
   Talk about deliberately engineering the sample data so one shift stays
   *partially filled* — because a demo that only shows a perfect match hides the
   feature that matters most: honestly flagging gaps and drafting the "help
   needed" broadcast.

7. **What you'd do next**
   e.g. two-way integration (Slack/SMS), recurring shifts, volunteer reliability
   history, calendar sync.

8. **Close + links**
   Link the public repo and the demo video.

## Checklist

- [ ] Title contains "Agents for Humans".
- [ ] Publicly published on builder.aws.com **before** the deadline.
- [ ] Includes at least one code snippet showing the Strands agent/tool.
- [ ] Links to the public repo and demo video.
- [ ] (Optional) Publish a second, different post — the rules allow more than one.
