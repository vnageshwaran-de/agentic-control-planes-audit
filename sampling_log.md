# Sampling Log — Empirical MCP Audit

**Audit date:** 2026-05-06
**Tool used:** Chrome MCP browser navigation against public GitHub repositories.

## A. Sampling sources

1. `modelcontextprotocol/servers` — official reference servers in `src/`. Visited 7 of 7 servers present at audit date (everything, fetch, filesystem, git, memory, sequentialthinking, time).
2. `punkpeye/awesome-mcp-servers` — curated community list with ~1,545 GitHub repository links.
3. Direct visits to well-known vendor-published MCP servers based on the steering-group community list and public ecosystem awareness.

## B. Inclusions (N=24)

See `audit_data.csv` for the full list with repository URLs. Categories represented:

- Reference (7): everything, fetch, filesystem, git, memory, sequentialthinking, time
- Data store (5): supabase, snowflake, mongodb, clickhouse, brave-search
- Cloud platform (3): cloudflare, heroku, awslabs
- Dev tools (1): github
- Observability (2): sentry, grafana
- Browser automation (1): playwright
- Knowledge management (1): notion
- Search (1 — also dual-counted as data store above): elasticsearch
- Payments (1): stripe-agent-toolkit
- Scraping/automation (1): apify
- Integration (1): membrane

## C. Exclusions

- `AgentDeskAI/browser-tools-mcp` — repo banner declares the project no longer active at audit date.
- `Azure/azure-mcp` — repo archived 2025-08-25; superseded by `microsoft/mcp` catalog (which is itself a meta-repo, not a single server).
- `sentry-protocol/sentry-mcp` — URL returns 404; correct repo is `getsentry/sentry-mcp` (included).
- `notionhq/notion-mcp-server` — URL returns 404; correct repo is `makenotion/notion-mcp-server` (included).
- `atlassian-labs/atlassian-mcp-server` — URL returns 404 at audit time.
- `microsoft/dataverse-mcp` — repo present but README is a stub announcement (≤200 words) and excluded by §C of `methodology.md`.
- `jaipandya/postgres-mcp-pro` — URL returns 404 at audit time.
- `Block/goose` — redirects to `aaif-goose/goose`, which is a *client* / agent framework, not an MCP server; excluded by §C.
- `jlowin/fastmcp` (`PrefectHQ/fastmcp`) — SDK / framework, not an MCP server; excluded by §C.

## D. Reproducibility

The exact set of repositories visited and signal extractions are recorded as Chrome-MCP browser_batch transcripts in this session's history. A successor session re-running the same URLs will obtain comparable signals modulo repo evolution between the audit date and the re-run. The rubric in `methodology.md §D` is deterministic for the 0/1 boundaries (presence/absence of typed schema, OAuth / API key strings, release-tag links) and uses documented prose-vs-config heuristics for the 1/2 boundaries.

## E. Suggested expansion

To scale from N=24 to a population estimate against MCPCORPUS (~14K servers), the rubric's signal extraction can be automated as a script that walks GitHub README + release-page HTML for each repo and applies the regex patterns in `methodology.md §D`. The pilot's role is to validate the rubric and surface the common-gap clusters; the population-scale audit is left as future work and noted as such in §IX of the manuscript.
