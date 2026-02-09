# Investment Intelligence Extractors (PoC Monorepo)

This repo is a proof-of-concept Python monorepo that extracts, normalizes, and prepares structured investment intelligence data from multiple sources.

- Packages live under `packages/`.
- Each package is independently installable (`pip install -e ...`).
- Each package emits **normalized JSONL**.

## Part 1 — Research & data source analysis

### TechCrunch

**Summary (2–4 bullets)**
- Extractable: article + media metadata via RSS (title, link, published time, author, categories/tags, short summary/description, GUID).
- Free access: yes via TechCrunch-provided RSS feeds (no auth / API key).
- Access method: consume RSS feeds (e.g. main feed, category feeds, tag feeds) and link back to the canonical article URLs.
- Rules: RSS use is explicitly governed by TechCrunch “RSS Terms of Use” (attribution + link back; don’t modify feed content or insert ads). General site Terms of Service restrict automated extraction/scraping.

**What data is available**
- RSS 2.0 feeds provide a stream of items including: `title`, `link`, `pubDate`, `dc:creator` (author), `category` (multiple), `guid`, and `description` (summary). Category and tag feeds exist (useful for investment-intel topics like startups/venture/fundraising).

**Free vs paid**
- RSS feeds are available without payment or credentials.
- TechCrunch does not present a public “developer API” equivalent to Crunchbase/Reddit for structured programmatic access; the PoC uses RSS as the supported syndication mechanism.

**Access details (endpoints / auth / limits)**
- Auth: none for RSS.
- Common RSS endpoints:
  - Main feed: `https://techcrunch.com/feed/`
  - Category feed example: `https://techcrunch.com/category/startups/feed/`
  - Tag feed example: `https://techcrunch.com/tag/fundraising/feed/`
- Parameters: none (RSS is retrieved via simple HTTP GET).
- Rate limits: not published for RSS; feeds declare an update cadence (e.g. WordPress `sy:updatePeriod`/`sy:updateFrequency`). Be polite and cache responses.

**How to access it (rules/ToS notes)**
- Prefer RSS feeds (explicitly supported) rather than scraping full HTML pages.
- If you use RSS, follow TechCrunch’s RSS terms (attribution + link; no modifying feed content or inserting ads).
- If you do crawl the site, consult robots.txt and the Terms of Service; some automated extraction is restricted.

**Source URLs**
- RSS Terms of Use: https://techcrunch.com/rss-terms-of-use/
- Terms of Service: https://techcrunch.com/terms-of-service/
- robots.txt: https://techcrunch.com/robots.txt
- Main RSS feed: https://techcrunch.com/feed/
- Category feed example: https://techcrunch.com/category/startups/feed/
- Tag feed example: https://techcrunch.com/tag/fundraising/feed/

### Crunchbase

**Summary (2–4 bullets)**
- Extractable: organizations/companies, people, funding rounds, acquisitions, investors + rich relationships (“cards”) via entity lookup.
- Official API access: requires an API key and is tied to a plan/license (Basic is limited; full API requires Enterprise/Applications license).
- Public web access (no key): organization pages may be blocked (often `403`) and are not a stable “free API”; if you do any analysis without a key, prefer local HTML snapshots and explicit “unavailable” behavior.
- Access method: official REST API at `https://api.crunchbase.com/v4/data/` using `user_key` or `X-cb-user-key`, subject to licensing/attribution terms.
- Limits: 200 calls/min; Search API default 50 results, `limit` up to 1000 with keyset pagination (`after_id`/`before_id`).

**What data is available**
- Company/organization, people, funding rounds, acquisitions, investors, categories, locations, plus “cards” (relationships) on entity lookup; Crunchbase states “over 600 endpoints” across Fundamentals/Insights/Predictions packages.

**Free vs paid**
- Access to the full API requires a paid license (Enterprise or Applications). Crunchbase Basic plans are limited to a small “Basic APIs” subset.
- Even the Basic APIs still require an API key.

**Access details (endpoints / auth / limits)**
- Auth: token-based; pass API key via `user_key` query param or `X-cb-user-key` header.
- Base URL: `https://api.crunchbase.com/v4/data/`.
- Rate limit: 200 calls/minute.
- Basic APIs (limited org fields) include:
  - Organization search: `https://api.crunchbase.com/api/v4/searches/organizations`
  - Organization entity lookup: `https://api.crunchbase.com/api/v4/entities/organizations/{permalink}`
  - Autocomplete: `https://api.crunchbase.com/api/v4/autocompletes`
- Search APIs: `POST /v4/data/searches/{collection}`; request body supports `field_ids`, `query` predicates (AND-only), optional `order`, and `limit`.
  - Default 50 results; `limit` max 1000.
  - Keyset pagination via `after_id` / `before_id`.
- Entity Lookup APIs: `GET /v4/data/entities/{collection}/{entity_id}` with `field_ids` and `card_ids`.
  - Card results return max 100 items per card; more via `/entities/{collection}/{entity_id}/cards/{card_id}`.

**How to access it (rules/ToS notes)**
- Use the official API with a license/key; do not scrape unless your license/terms explicitly permit.
- The docs also specify attribution requirements when sharing Crunchbase-derived data.

**Source URLs**
- Docs home: https://data.crunchbase.com/docs
- Using the API (auth, base URL, rate limits, terms): https://data.crunchbase.com/docs/using-the-api
- Basic APIs overview: https://data.crunchbase.com/docs/crunchbase-basic-using-api
- Search API guide (limits, pagination): https://data.crunchbase.com/docs/using-search-apis
- Entity lookup guide (cards, limits): https://data.crunchbase.com/docs/using-entity-lookup-apis
- Autocomplete guide: https://data.crunchbase.com/docs/using-autocomplete-api
- API reference: https://data.crunchbase.com/reference

### Reddit

**Summary (2–4 bullets)**
- Extractable: posts/comments, subreddit metadata, and search/listing feeds (e.g. `/new`, `/hot`, `/search`) as JSON “Listings”.
- Free access: yes for eligible free usage, but registration + OAuth are required and Reddit enforces rate limits/throttling.
- Access method: OAuth2 + descriptive `User-Agent`, using `https://oauth.reddit.com` endpoints; monitor `X-Ratelimit-*` headers.
- Limits: 100 QPM per OAuth client id for free usage (averaged); listing `limit` max 100.

**What data is available**
- Posts, comments, subreddit metadata, search results, listing endpoints (`/hot`, `/new`, `/top`, etc.), and structured JSON responses (Listings with `after`/`before` pagination).

**Free vs paid**
- The Data API supports free access under rate limits; Reddit reserves the right to charge fees in the future and may require separate agreements for higher-volume/commercial use.

**Access details (endpoints / auth / limits)**
- Clients must authenticate with OAuth2 (Reddit explicitly notes they can throttle/block unidentified users).
- Rate limit (free access): **100 queries per minute per OAuth client id** (averaged over a time window) and rate-limit headers:
  - `X-Ratelimit-Used`, `X-Ratelimit-Remaining`, `X-Ratelimit-Reset`.
- Listings: use `after`/`before`, `limit` (max 100), `count`, `show`.
- Search endpoint shape (listing): `GET /r/{subreddit}/search` with params like `q`, `restrict_sr`, `sort`, `t`, `limit`.
- JSON: legacy encoding can be opted out with `raw_json=1`.

**How to access it (rules/ToS notes)**
- Register, create credentials, use OAuth tokens, and set a unique/descriptive `User-Agent`.
- Data API Terms include restrictions around User Content use and emphasize compliance requirements.

**Source URLs**
- API documentation: https://www.reddit.com/dev/api/
- Reddit API access wiki (register + create credentials): https://www.reddit.com/r/reddit.com/wiki/api/
- Reddit Data API Wiki (rules + 100 QPM + rate headers): https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki
- Data API Terms: https://www.redditinc.com/policies/data-api-terms

## Part 2 — Proof-of-concept packages

### Install

```bash
python3 -m pip install -e packages/techcrunch_extractor
python3 -m pip install -e packages/reddit_extractor

# Crunchbase (choose one):
# - No API key (public web only; often blocked):
python3 -m pip install -e packages/crunchbase_intel
# - Paid API key required:
python3 -m pip install -e packages/crunchbase_extractor
```

### TechCrunch (RSS) example

```bash
techcrunch-extractor extract --rss-url https://techcrunch.com/feed/ --limit 25 --out tc.jsonl
```

### Reddit example

Create a Reddit app and obtain an access token (or set up refresh-token flow), then:

```bash
export REDDIT_ACCESS_TOKEN="..."
export REDDIT_USER_AGENT="macos:newsletter_packages:poc (by /u/YOUR_USERNAME)"
reddit-extractor extract --subreddit startups --query "seed round" --limit 25 --out reddit.jsonl
```

### Crunchbase example

#### Option A: No API key (public web / snapshots) — `crunchbase-intel`

Live organization URLs are frequently blocked (e.g. `403`). For correctness-first work without escalating scraping, prefer local HTML snapshots.

Parse a saved HTML file:

```bash
crunchbase-intel org --html-file packages/crunchbase_intel/tests/fixtures/user/<org>.html
```

Attempt a live fetch (expect structured failures if blocked):

```bash
crunchbase-intel org --url "https://www.crunchbase.com/organization/crunchbase"
```

#### Option B: Paid API access — `crunchbase-extractor`

```bash
export CRUNCHBASE_USER_KEY="..."
crunchbase-extractor autocomplete --query "airbnb" --collection-ids organization.companies --limit 5
crunchbase-extractor organization --permalink tesla-motors --out tesla.jsonl
crunchbase-extractor funding-rounds --announced-on-gte 2025-01-01 --money-raised-gte 10000000 --currency usd --limit 100 --out rounds.jsonl
```
