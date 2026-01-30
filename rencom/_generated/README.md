# Auto-Generated Code

⚠️ **DO NOT EDIT FILES IN THIS DIRECTORY MANUALLY**

All code in this directory is automatically generated from the Rencom API's
OpenAPI specification. Any manual changes will be overwritten the next time
code generation runs.

## What's in here?

- `models.py` - Pydantic models for request/response schemas
- `api/` - Low-level API client methods that directly call endpoints
- `types.py` - Type aliases and enums

## How to regenerate

Run the generation script from the repository root:

```bash
python scripts/generate.py
```

This will:
1. Download the latest OpenAPI spec from the API
2. Generate Python code from the spec
3. Place generated files in this directory

## Making changes

If you need to change something in the generated code:

1. **For model changes**: Update the API's Pydantic models in the rencom-api repo
2. **For endpoint changes**: Update the API's FastAPI route definitions
3. **For SDK features**: Add wrapper code in the parent `rencom/` directory

The SDK architecture separates generated code (this directory) from hand-crafted
wrapper code (parent directory). This ensures the SDK stays in sync with the API
while providing a great developer experience.
