# Case: ssv2-typed-parameters

## Requirement or fault

An SSP2 `ParameterSet` 2.0 document must auto-detect as version 2.0 and preserve
a 3x2 matrix parameter with two dimensions, arrays, and several scalar types
through a read.

## Level

component (SSV codec and SSP2 facade).

## Input provenance

Hand-authored here, SSP2 `ParameterSet` 2.0, named `Example`.

## Independent oracle

`src/pyssp_standard/schema/SSP2/SystemStructureParameterValues.xsd`; the facade
read itself pins the parsed model shape, and the SSP2 round-trip tests re-read
what the library wrote.

## Comparison

Parsed structure: version, parameter count, dimension sizes, names and types.

## Update policy

Reviewed with a change to SSP2 parameter parsing; never auto-updated.

## What this case proves

That SSP2 parameter sets are read through the same facade as SSP1 without losing
dimensions or typed values. Without it, SSP2 support is untested on real input.
