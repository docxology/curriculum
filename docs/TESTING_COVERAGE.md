# Tests and coverage

The project keeps [native tests](../tests/README.md) for configuration,
outline parsing, file layout, content processing, site generation, and the
model-backed stages. The configured test markers are in
[`pytest.ini`](../pytest.ini). Use collection output for the current counts.

```bash
uv run --no-sync python -m pytest --collect-only -q
```

## File-based verification

The [setup guide](SETUP.md#verify-local-authoring-and-website-assembly) lists
the selected native tests that can run without Ollama. They cover real inputs
and generated HTML. They verify the behavior of the parser and website
builder. They do not measure the factual accuracy or teaching value of
model-generated lessons.

Use the [offline fixture](OFFLINE_FIXTURE.md) to repeat the website build
with the same retained inputs. Inspect module and session navigation and
check that material buttons appear only where files are present.

## Service-backed verification

The full suite loads [the test configuration](../tests/conftest.py), which
can probe or start local Ollama and query the configured model. The
[validation guide](VALIDATION.md) describes the broader Stage 02 reports.
Treat coverage as specific to the tests and service setup that actually ran.
