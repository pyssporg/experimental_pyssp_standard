"""Version-neutral protocols that facades and consumers share.

``tree`` describes the SSD model tree and ``parameters`` describes parameter
sets and mappings, both as structural protocols satisfied by the SSP1 and SSP2
dataclasses. These modules must not import ``pyssp_standard.standard``: they
outline the public contract, they do not depend on a versioned stack.
"""
