from __future__ import annotations

from pathlib import Path

from pyssp_standard.common.xml_schema_validation import XmlSchemaValidator, resolve_schema_path
from pyssp_standard.standard.fmi2.model.model_description import Fmi2ModelDescriptionDocument


DEFAULT_FMI2_MODEL_DESCRIPTION_SCHEMA_PATH = resolve_schema_path("FMI2", "fmi2ModelDescription.xsd")


class Fmi2ModelDescriptionSchemaValidator(XmlSchemaValidator):
    def __init__(self, schema_path: Path | None = None):
        super().__init__(
            schema_path or DEFAULT_FMI2_MODEL_DESCRIPTION_SCHEMA_PATH,
            error_prefix="FMI2 modelDescription XML failed XSD validation",
        )


class Fmi2ModelDescriptionSemanticValidator:
    def validate(self, model: Fmi2ModelDescriptionDocument) -> None:
        if model.fmi_version != "2.0":
            raise ValueError(f"Unsupported FMI version '{model.fmi_version}'")
        if model.interface_type is None:
            raise ValueError("FMI2 modelDescription must declare ModelExchange or CoSimulation")

        seen_names: set[str] = set()
        for variable in model.variables:
            if variable.name in seen_names:
                raise ValueError(f"Duplicate variable '{variable.name}'")
            seen_names.add(variable.name)

        for type_definition in model.type_definitions:
            if type_definition.type_name == "Enumeration" and not type_definition.enumeration_items:
                raise ValueError(f"Enumeration type '{type_definition.name}' must define at least one Item")

    def validate_binary(self, model: Fmi2ModelDescriptionDocument, binary_name: str) -> None:
        if model.fmi_version != "2.0":
            raise ValueError(
                f"fmiVersion '{model.fmi_version}' is not a valid FMI 2.0 version"
            )
        if model.interface_type is None or model.capabilities is None:
            raise ValueError("modelDescription must declare a valid FMI 2.0 interface")
        if model.capabilities.model_identifier != Path(binary_name).stem:
            raise ValueError(
                f"modelIdentifier '{model.capabilities.model_identifier}' "
                f"does not match binary '{binary_name}'"
            )


class Fmi2ModelDescriptionValidator:
    def __init__(
        self,
        *,
        schema_validator: Fmi2ModelDescriptionSchemaValidator | None = None,
        semantic_validator: Fmi2ModelDescriptionSemanticValidator | None = None,
    ):
        self.schema_validator = schema_validator or Fmi2ModelDescriptionSchemaValidator()
        self.semantic_validator = semantic_validator or Fmi2ModelDescriptionSemanticValidator()

    def validate(self, model: Fmi2ModelDescriptionDocument, xml_text: str) -> None:
        self.semantic_validator.validate(model)
        self.schema_validator.validate_xml(xml_text)
