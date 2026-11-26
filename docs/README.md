# Curriculum documentation

## Author a course

- [Setup](SETUP.md) installs and verifies the environment.
- [Configuration](CONFIGURATION.md) explains the course, model, and output YAML files.
- [JSON outline](JSON_OUTLINE.md) describes the contract between the outline
  and material stages.
- [Content formats](FORMATS.md) describes session files and review checks.
- [Offline fixture](OFFLINE_FIXTURE.md) shows how to build a site from an existing
  outline, lecture, and Mermaid source.

## Operate the pipeline

- [Pipeline guide](PIPELINE_GUIDE.md) lists stage commands and inputs.
- [Deployment](DEPLOYMENT.md), [logging](LOGGING.md), and
  [troubleshooting](TROUBLESHOOTING.md) cover operations.
- [Validation](VALIDATION.md) and [testing](TESTING_COVERAGE.md) explain the
  available checks and dependencies.
- [Security](SECURITY.md) covers handling of configuration and generated content.

## Develop and reproduce

- [Architecture](ARCHITECTURE.md), [data flow](DATA_FLOW.md), and
  [module organization](MODULE_ORGANIZATION.md) explain how the stages fit together.
- [API](API.md), [extensions](EXTENSION.md), [error handling](ERROR_HANDLING.md),
  [performance](PERFORMANCE.md), and [contributing](CONTRIBUTING.md) cover implementation.
- The [canonical manuscript](manuscript/README.md) documents the observed
  fixture and the pinned rendering commands.
- [Historical project notes](other/README.md) include the
  [earlier manuscript scope audit](other/curriculum_manuscript_scope_audit.md).
