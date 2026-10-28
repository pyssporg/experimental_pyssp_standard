# Case: ssv-external-parameter-set

## Requirement or fault

An SSP1 `ParameterSet` 1.0 document must validate and must resolve the external
binding in `ssd-mixed-parameter-bindings/input.ssd`, including after the archive
layer persists an edited value back into the archive.

## Level

component (SSV codec and facade), system (persisted archive parameter set).

## Input provenance

Hand-authored here, SSP1 `ParameterSet` 1.0, named `ControllerExternal`. It is
the file the mixed SSD refers to as `external_values.ssv`.

## Independent oracle

`src/pyssp_standard/schema/SSP1/SystemStructureParameterValues.xsd` via
`SSV.check_compliance()` in `tests/ssp1/facade/test_ssv_ssp1.py`.

## Comparison

Parsed parameter names, types, and values; the archived copy is compared after a
write-and-reopen cycle.

## Update policy

Reviewed with a codec or archive change that alters parameter-set semantics;
never auto-updated.

## What this case proves

That external parameter sets survive validation, resolution, edit, and archive
persistence. Deleting it breaks the external-binding evidence for SSP1.
