# Educational Course Generator

Curriculum turns course specifications into outline JSON and session-level
materials. Authors can supply hand-written Markdown and Mermaid sources.
The optional local Ollama stages draft outlines and content. The static site
builder uses an existing outline and files without contacting a model.

- [Documentation](docs/README.md) covers setup, authoring, operations, and verification.
- [Offline fixture walkthrough](docs/OFFLINE_FIXTURE.md) builds a small site from checked-in inputs.
- [Technical manuscript](docs/manuscript/README.md) describes the handoff between outline, materials, and website.

From the repository root, install the checked-in environment with
`uv sync --locked --extra dev`. Start with the [setup guide](docs/SETUP.md)
and use the [pipeline guide](docs/PIPELINE_GUIDE.md) for model-backed stages.

## Citation and archive

The historical repository archive is available through its
[Zenodo DOI](https://doi.org/10.5281/zenodo.17954165). See
[CITATION.cff](CITATION.cff) for the software author and repository.
The [license](LICENSE) is Creative Commons Attribution-NonCommercial-NoDerivatives
4.0 International.
