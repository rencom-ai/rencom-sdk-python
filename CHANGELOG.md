# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2026-01-30

### Fixed
- README example: Use correct field names (`.merchants` not `.results`, `.products` not `.results`)
- Examples: Fixed and uncommented `ucp_search.py` with correct field names

## [0.1.2] - 2026-01-30

### Fixed
- UCP merchant search endpoint: Changed from `/ucp/v1/merchants/search` to `/ucp/v1/merchants` to match API

## [0.1.1] - 2026-01-30

### Fixed
- GitHub workflow: Made Codecov upload optional (no longer fails if token is missing)
- GitHub workflow: Removed Python 3.9 from test matrix (package requires >=3.10)

## [0.1.0] - 2026-01-29

Initial release.

### Added
- x402 resource search client
- UCP merchant and product discovery clients
- Authentication flows (API key, JWT, magic link)
- Rate limiting and error handling
- Auto-pagination support
- Analytics tracking (sessions, clicks)
- Comprehensive test suite
- Full type hints and Pydantic models
- Auto-generation from OpenAPI spec
- HTTP/2 support via httpx[http2]

### Changed
- Simplified README

### Fixed
- Analytics fields (`search_appearances`, `click_count`) now correctly map to database columns
