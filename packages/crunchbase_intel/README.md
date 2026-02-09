# crunchbase-intel

Transparency-first, academic Crunchbase-focused extractor intended to support *human* investigative analysis of startups, investors, and investment activity.

This project prioritizes **correctness, provenance, and legal/ethical constraints** over completeness.

## What this package does

- Extracts **publicly visible** information from Crunchbase organization pages (when accessible without login).
- Normalizes outputs into small, explicit models (`Company`, `FundingRound`, `Investor`) suitable for later knowledge-graph ingestion.
- Captures **provenance** for every extraction result (source, method, timestamp, URL).
- Returns structured **"unavailable"** fields when data cannot be accessed safely.

## Critical constraints (by design)

1. **No paid Crunchbase API assumptions**
   - This package does *not* require an API key.
   - It does not rely on private or paid endpoints.

2. **No aggressive scraping**
   - Requests are single-page and rate-limited.
   - No cookies, no authenticated sessions, no bypassing protections.

3. **No fabricated data**
   - If a field cannot be extracted from the input page, the field stays `null` and a corresponding `unavailable` entry explains why.

## What data is usually available (when public pages permit)

From an organization page, this package attempts to extract:
- Company name
- Canonical Crunchbase URL (and other URLs if presented as structured data)
- Short description (if present in structured markup)

Funding rounds, investors, and people/roles are often **not reliably available without paid/API access** and/or may be rendered dynamically. In such cases, the extractor returns those sections as unavailable.

## Legal / ethical note

Crunchbase content and access patterns are governed by Crunchbase’s terms. This package is designed to be *polite and minimal* and to fail clearly when access is restricted.

If you plan to run this at scale, **do not**: (a) increase concurrency, (b) ignore rate limits, or (c) attempt to evade blocks.

## CLI

Extract a company record from a Crunchbase organization URL:

```bash
crunchbase-intel org --url "https://www.crunchbase.com/organization/crunchbase"
```

Parse a saved HTML file (useful for reproducible academic analysis):

```bash
crunchbase-intel org --html-file path/to/page.html
```

## Fixture capture workflow (recommended)

Crunchbase commonly returns `403` to automated requests for organization pages. To do correctness-focused work without bypassing protections, use **local HTML snapshots**.

1) Open the organization page in your browser (interactive, logged-out is fine).
2) Save the page HTML (e.g., *File → Save Page As…*).
3) Put the saved file at:

`packages/crunchbase_intel/tests/fixtures/user/<org>.html`

This folder is ignored by git by default.

Then run:

```bash
crunchbase-intel org --html-file packages/crunchbase_intel/tests/fixtures/user/<org>.html
```

This keeps results reproducible and avoids any scraping escalation.

## Testing

Tests use local fixtures only. They validate:
- No silent failures (errors are explicit)
- Provenance always exists
- Missing fields are marked as unavailable rather than fabricated

### Optional: snapshot test (user-provided)

If you have a local snapshot you want validated by tests, set:

```bash
export CRUNCHBASE_INTEL_SNAPSHOT_HTML="packages/crunchbase_intel/tests/fixtures/user/anthropic.html"
```

Then run `pytest`. The snapshot test is skipped if the env var is missing.

### Optional: live integration test mode (explicitly gated)

To verify that live org URLs fail **explicitly and structurally** (e.g., `403` access denied) without making CI flaky, integration tests are skipped unless you opt in:

```bash
export CRUNCHBASE_INTEL_INTEGRATION=1
pytest
```

If Crunchbase happens to allow access from your environment, the integration test will skip rather than make a brittle claim.

