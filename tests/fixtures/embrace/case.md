# Case: embrace

The EMBRACE project example SSP, kept byte-for-byte as published.

## Requirement or fault

Archive, codec, and facade code must read and preserve a real tool-generated
SSP: 76 connectors, FMU resources, an external SSV binding, an SSM mapping, and
an OMSimulator namespace on `SystemStructure.ssd`.

## Level

component (codec and facade over real documents), system (archive round trips),
acceptance (deterministic re-serialization).

## Input provenance

Verbatim third-party: the EMBRACE project example SSP. `SystemStructure.ssd`
declares the OMSimulator namespace (`xmlns:oms`), so it is tool-generated rather
than authored here. Internal filenames are unchanged because
`SystemStructure.ssd` and the `.ssm` refer to them.

## Independent oracle

`src/pyssp_standard/schema/SSP1/SystemStructureDescription.xsd` via
`SSD.check_compliance()`, plus the matching SSP1 XSDs when the `.ssm` and `.ssv`
resources are loaded.

## Comparison

Parsed structure for connector and binding counts; exact re-serialization for
round-trip tests; SHA-256 equality between repeated archive builds for the
determinism tests.

## Update policy

Never edited by hand. Replaced only by a fresh verbatim copy of the EMBRACE
example, reviewed as a whole with the tests that consume it.

## What this case proves

That the library reads and preserves an SSP produced by another tool, not just
the minimal documents authored in this repository. Deleting it would leave all
archive and codec evidence resting on hand-written XML.
