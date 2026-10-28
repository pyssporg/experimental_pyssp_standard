# Case: srmd-easyssp-sample

## Requirement or fault

An SRMD document exported by easySSP must parse and pass the SRMD compliance
validator, keeping its classifications and metadata intact.

## Level

component (SRMD codec), unit (SRMD validation).

## Input provenance

Verbatim third-party: exported by easySSP (`generationTool`,
`generationDateAndTime="2024-02-06T13:21:41Z"`), kept unchanged.

## Independent oracle

`SRMD.check_compliance()` and `Ssp1SrmdValidator`, which implement the SRMD
structural rules directly because the traceability schema ships no loadable XSD
for this check.

## Comparison

Parsed structure: version, name, classification type, and classification entry
keyword; compliance returns true.

## Update policy

Never edited. Replaced only by a fresh verbatim easySSP export, reviewed with
the SRMD tests.

## What this case proves

That SRMD parsing and compliance work on a real exporter's output rather than
only on documents built inside the tests.
