# Methods

We supply the repository's example JSON outline to the Stage 06 website
command and choose an explicit HTML destination in a temporary directory.
We use the real configuration loader to determine the course directory
key. The fixture JSON omits the optional course-template field, so the
loader derives the key from the default course YAML.

We place the example lecture and Mermaid source in the slugged directory
for the first module and its first session. We leave all other session
directories absent. The builder reads the module titles, session titles,
and ordering from JSON. It scans the course-specific directories for
materials by filename, translates Markdown to HTML, and embeds available
Mermaid source for processing by the browser. The fixture invokes neither
outline drafting nor material generation.

After generation, a standard-library HTML parser counts the module,
session, and material buttons. It checks that the lecture and diagram
buttons both identify the intended session. It also checks that the
lecture's Cell Theory heading appears in the document.
