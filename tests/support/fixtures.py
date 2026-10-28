"""Fixture paths, resolved from this file so they do not depend on the cwd."""

from __future__ import annotations

from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"

EMBRACE = FIXTURES / "embrace"
EMBRACE_SSD = EMBRACE / "SystemStructure.ssd"
EMBRACE_SSM = EMBRACE / "resources" / "ECS_HW.ssm"
EMBRACE_FMU_DIR = EMBRACE / "resources" / "0001_ECS_HW"
EMBRACE_MODEL_DESCRIPTION = EMBRACE_FMU_DIR / "modelDescription.xml"

MIXED_SSD = FIXTURES / "ssd-mixed-parameter-bindings" / "input.ssd"
EXTERNAL_SSV = FIXTURES / "ssv-external-parameter-set" / "input.ssv"
SSV2 = FIXTURES / "ssv2-typed-parameters" / "input.ssv"
SRMD = FIXTURES / "srmd-easyssp-sample" / "input.srmd"
TEXT_PAYLOAD = FIXTURES / "payload-plain-text" / "input.txt"
