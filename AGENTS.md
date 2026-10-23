# AGENTS

## Vision first (required)

Before you read code, edit files, or plan a change, read the project vision:

**`product-breakdown/00-intent/purpose.md`**

It states why this library exists, what it commits to, and what it refuses to
become. `users.md` and `constraints.md` in the same folder carry the rest of the
intent layer. It is the first document to read, not a reference of last resort.

- Read `purpose.md` in full before making any change to code, tests, docs, or
  artifacts.
- Judge every proposed change against it. If a change conflicts with the vision,
  its commitments, goals, or non-goals, stop and surface the conflict; do not
  implement it silently.
- If the work shows the long-term direction is wrong, change the vision
  deliberately first, then the code. Never let the repository drift away from
  its stated intent.

## Rules

1. **Don't assume. Surface tradeoffs.** If a contract is ambiguous, stop and say
   so rather than picking a behaviour silently.
2. **Minimum code that solves the problem.** Nothing speculative.
3. **Touch only what you must.** Clean up only your own mess.
4. **Define success criteria and verify.**

## Repository Focus

`pyssp_standard` is a Python library for inspecting, creating, and editing SSP
and FMI artifacts: `.ssp`, `.ssd`, `.ssv`, `.ssm`, `.fmu`, and
`modelDescription.xml`. It is a pre-processing and controlled-edit library, not
a full authoring environment or a simulation runtime.

- The public facades are listed in `pyssp_standard/__init__.py`; consumers use
  those, not internal codecs or schema bindings.
- The package is layered: archive, codec, model, validation, orchestration, and
  public API each own one concern.

## Hard constraints

- **Stay layered.** `product-breakdown/02-architecture/layer-rules.md` defines
  what each layer may and may not do; do not move work upward into a facade.
- **The artifact is the preferred border.** When a Python object must cross,
  expose only a documented public facade or model type from the package public
  surface.
- **Internal shapes stay internal.** Codecs, schema bindings, and archive
  helpers do not leak into the model or the public API.
- **Compliance is explicit.** `check_compliance()` is never run implicitly.
- **Round-trip preservation.** Codecs preserve element order, annotations, and
  extensions.
- **Standard library XML.** Parse with `xml.etree.ElementTree`; do not add lxml
  or another XML dependency.

## Code guidelines

- Keep it simple.
- Minimize duplication.
- Keep files small and focused.
- A unit or function should stay at a common level of abstraction.

This is experimental software:

- Interfaces do not need to be stable; prioritize clarity and ease of use.
- Avoid thin shims or wrappers; change the references directly.

## Conventions

- `product-breakdown/` holds current state; keep it in step with the code.
- Keep docs short, focused, and single-purpose.
- Prefer adding a new focused page over growing a mixed-purpose page.
- Treat `README.md` as a landing page, not a full manual.
- Keep the main onboarding flow in `docs/getting_started.md`.
- Keep reference material in `docs/command_reference.md`, not in onboarding
  pages.
- Organize docs by audience: `docs/user/` for user workflows, `docs/dev/` for
  maintainer and implementation notes, `docs/integrations/` for external system
  integrations.
- Strongly prefer canonical pages over compatibility stubs or redirect files.
- When moving docs, update links to the new destination and remove obsolete
  references.
- Optimize for the easiest first success: show the lowest-friction path before
  the full rebuild path.
- Scope prerequisites to the workflow that actually needs them.
- Avoid duplication across pages. If two pages repeat the same explanation,
  keep it in one page and link to it.
- Start pages with what the reader can do there and who the page is for.
- Keep filenames stable and descriptive.
- Use `docs/index.md` as the main documentation router.

## Environment

- Python >= 3.10.
- Use the repo-local `venv` when it exists. Prefer
  `. venv/bin/activate && <command>` over the system Python for `pytest`,
  `python -m ...`, and related tooling.
- Tests: `pytest` (`pytest.ini` sets `testpaths = pytest`). Run a category with
  `pytest pytest/ssp1/`, `pytest pytest/fmi2/`, `pytest pytest/ls_ref/`, or
  `pytest pytest/tools/`.

## Reading scope

Keep repository context narrow. Do not scan the whole repo by default.

After the vision, read in this order:

- `product-breakdown/03-implementation/code-structure.md`
- `pyssp_standard/__init__.py`
- the specific module under `pyssp_standard/` that matches the task
- the smallest relevant test under `pytest/`
- `README.md` only for package positioning, not for implementation details

Use `product-breakdown/03-implementation/code-structure.md` for first-pass
orientation. Open `product-breakdown/02-architecture/component-view.md` only
when the task needs architectural background beyond the repo map.

Default working set:

- `pyssp_standard/`
- `pytest/`
- `docs/` only when the task is documentation-related

Avoid reading these paths unless the task explicitly requires them:

- `venv/`
- `.git/`
- `.pytest_cache/`
- `__pycache__/`
- `3rdParty/`
- `pytest/legacy_unsupported/`
- `pyssp_standard/schema`
- large binary or archive fixtures such as `*.fmu`, `*.ssp`, `*.zip`

For tests, do not scan all fixtures up front. Open only the fixture files
referenced by the test you are editing.

Search strategy:

- Prefer targeted `rg` queries scoped to `pyssp_standard/` or a specific
  `pytest/` file.
- Prefer opening one file at a time over reading complete directories.
- Do not read vendored standards or generated/cache content for general feature
  work.
