# Test Fixtures

This directory contains test fixtures and recorded HTTP responses.

## VCR Cassettes

The `vcr_cassettes/` directory contains recorded HTTP responses using [VCR.py](https://vcrpy.readthedocs.io/).

### What are VCR Cassettes?

VCR cassettes record real HTTP interactions and replay them during tests. This allows:
- Fast tests without hitting the live API
- Consistent test results
- Testing against real API responses
- Working offline

### Recording New Cassettes

1. Ensure you have a valid `RENCOM_API_KEY` set
2. Run tests with VCR decorators - first run records, subsequent runs replay
3. Commit cassettes to git (but remove sensitive data first!)

### Example

```python
import vcr

@vcr.use_cassette('tests/fixtures/vcr_cassettes/x402_search.yaml')
async def test_x402_search():
    # First run: makes real API call and records to cassette
    # Subsequent runs: replays from cassette
    client = AsyncRencomClient(api_key="test")
    results = await client.x402.search("weather")
    assert len(results.results) > 0
```

### Security Note

VCR cassettes may contain sensitive information like API keys in headers.
Before committing cassettes, ensure:
- API keys are redacted
- Personal data is removed
- No secrets are exposed

Use VCR's filter options to automatically scrub sensitive data:

```python
@vcr.use_cassette(
    'test.yaml',
    filter_headers=['authorization', 'x-api-key']
)
```
