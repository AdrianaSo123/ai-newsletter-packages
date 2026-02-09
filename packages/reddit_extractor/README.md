# reddit-extractor

Reddit extractor and normalizer for investment intelligence.

## What it does

- Fetches posts from a subreddit either via search (`/search`) or via the `/new` listing.
- Emits normalized JSONL records.

## What it can/cannot extract

- Can extract: post metadata returned by the Reddit Data API (title, URL, author, timestamps, score, etc.).
- Cannot extract: private subreddits, deleted content, or anything blocked by API permissions/rate limiting.

## Constraints

- Requires OAuth credentials and a descriptive, unique `REDDIT_USER_AGENT`.
- Subject to Reddit rate limits; the CLI prints rate-limit info to stderr when available.

## Install (isolated)

```bash
cd packages/reddit_extractor
python3 -m poetry install
```

## Configure

At minimum:

```bash
export REDDIT_USER_AGENT="macos:newsletter_packages:poc (by /u/YOUR_USERNAME)"
```

Then provide either:

- `REDDIT_ACCESS_TOKEN`, or
- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_REFRESH_TOKEN`

## Run

```bash
python3 -m poetry run reddit-extractor extract --subreddit startups --query "seed round" --limit 25 --out reddit.jsonl
```

## Test

```bash
python3 -m poetry run pytest
```
