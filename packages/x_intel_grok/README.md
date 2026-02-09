# x-intel-grok

X (Twitter) source-specific package that fetches tweets via the **official X API** and analyzes them with **Grok (xAI)** using an OpenAI-compatible chat-completions endpoint.

## What it does

- Accepts tweet URLs or tweet IDs.
- Fetches tweet text and basic metadata via the official X API.
- Calls Grok (xAI) to produce a structured analysis.
- Emits one JSON object per tweet as JSONL.

## What it can/cannot extract

- Can extract: tweet text + metadata returned by the X API (subject to your access level).
- Cannot extract: anything that requires scraping or bypassing access controls. No HTML crawling.

## Constraints

- Requires X API access (`X_BEARER_TOKEN`).
- Requires xAI access (`XAI_API_KEY`).
- Subject to rate limits and policy constraints from both providers.

## Install (isolated)

```bash
cd packages/x_intel_grok
python3 -m poetry install
```

## Configure

```bash
export X_BEARER_TOKEN="..."
export XAI_API_KEY="..."

# Optional overrides
export X_API_BASE_URL="https://api.x.com/2"
export XAI_BASE_URL="https://api.x.ai"
export XAI_MODEL="..."
```

## Run

Analyze a single tweet URL:

```bash
python3 -m poetry run x-intel-grok analyze --tweet-url "https://x.com/user/status/1234567890" --out out.jsonl
```

Or provide a file with one URL/ID per line:

```bash
python3 -m poetry run x-intel-grok analyze --in-file tweets.txt --out out.jsonl
```

## Output (agent-friendly)

Each output line is a JSON object with:

- `ok`: boolean success
- `tweet_id`, `tweet_url`
- `tweet`: the tweet object returned by the X API (when available)
- `analysis`: parsed JSON from Grok when the model returns valid JSON
- `analysis_text`: raw model content when JSON parsing fails
- `grok`: full raw OpenAI-compatible response for provenance/debugging
- `provenance`: base URLs + model name

On partial failures (e.g. tweet not found, xAI error), the tool still emits a per-tweet record with `ok: false` and an `error` object.

## Test

```bash
python3 -m poetry run pytest
```

### Optional live smoke test (explicitly gated)

```bash
export X_INTEL_GROK_INTEGRATION=1
export X_BEARER_TOKEN="..."
export XAI_API_KEY="..."
export X_INTEL_GROK_TWEET_ID="1234567890"

python3 -m poetry run pytest -m integration
```
