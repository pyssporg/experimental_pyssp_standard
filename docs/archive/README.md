<!-- GENERATED FILE — do not edit. Regenerate with pb-registers. -->

# Decision Stream

Flat, dated history of every committed design choice. Current state lives
in the layer leaves named by each record's `state:` field.

Records live in the cold-storage archive; extract one with `pb archive read <ID>`.

## By Layer

### Implementation

- **DEC-001** — SSP FMU iteration API surface · accepted · 2026-05-26 · `DEC-001`
  FMU iteration over SSP components ships as an operations-layer function plus a thin SSP delegation method.
- **DEC-002** — Reproducible archive builds · accepted · 2026-06-10 · `DEC-002`
  Archive creation is deterministic by default, using FMI_EPOCH timestamps, sorted entries, and ZIP_DEFLATED.
- **IMD-001** — set_generation_date_and_time placement and scope · accepted · 2026-05-25 · `IMD-001`
  Each XML and archive facade sets generationDateAndTime itself, formatting through one shared utility.
- **IMD-002** — Public parameter-set and parameter-mapping contract · accepted · 2026-10-27 · `IMD-002`
  Parameter sets and mappings cross the library border as version-neutral Protocol types, not concrete SSP1 classes.
- **IMD-003** — Publish SSD model types and concrete parameter types at the package border · accepted · 2026-10-27 · `IMD-003`
  Consumers import pyssp_standard only through its top-level surface; the package publishes the SSD tree types and the concrete SSP1 parameter types.
- **IMD-004** — Replace the SSP1 tree classes with protocols and facade construction · accepted · 2026-10-27 · `IMD-004`
  The public surface carries no SSP version token; the SSD tree is protocols and every document is built through facade methods.
