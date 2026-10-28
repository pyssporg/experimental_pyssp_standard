"""User-facing, context-managed entry points for the supported artifacts.

Each module here owns one document or archive facade: ``ssp``, ``ssd``, ``ssv``,
``ssm``, ``fmu``, ``md``, ``ls_ref``, ``srmd``, and ``ssb``. Import them from
``pyssp_standard`` (``from pyssp_standard import SSP``) or, when the module
itself matters, from here (``from pyssp_standard.facades.ssp import SSP``).
"""
