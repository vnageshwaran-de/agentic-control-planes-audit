D6 reference-unit evidence
==========================
monorepo: github.com/modelcontextprotocol/servers
pinned SHA: c799c8552b0f27b7a33a7b9233773da144dddcf5

The seven reference servers (R01-R07) are released together from this monorepo;
their D6 (versioning/supply-chain) scores were adjudicated from the repository-ROOT
release configuration below, which sits OUTSIDE the per-server subpath snapshots in
snapshots_and_instruments.zip. Captured here at the pinned SHA so the seven D6
scores are reproducible without visiting the live repository.

Files: root_release.yml (OIDC trusted publishing + build provenance,
protected 'release' environment, SHA-pinned actions), root_version-packages.yml, root_prepare-python-release.yml, SECURITY.md.
(The 'root_' prefix marks these as the monorepo-root .github/workflows files, stored flat here.)
