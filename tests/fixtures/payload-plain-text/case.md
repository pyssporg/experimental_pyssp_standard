# Case: payload-plain-text

## Requirement or fault

Adding an arbitrary non-SSP payload to an archive must preserve its bytes and
its filename through add, list, and reopen.

## Level

system (archive orchestration).

## Input provenance

Hand-authored here: one line of Welsh prose with no schema meaning.

## Independent oracle

Payload only, no oracle needed because the tests assert the exact bytes and name
survive `SSP.add_resource` and archive round trips.

## Comparison

Exact bytes and exact resource name.

## Update policy

Contents may change freely as long as the tests still assert byte preservation;
the filename `input.txt` is the stable part.

## What this case proves

That the archive layer does not assume every resource is XML or an FMU. Without
it, a codec-shaped assumption in `add_resource` could go unnoticed.
