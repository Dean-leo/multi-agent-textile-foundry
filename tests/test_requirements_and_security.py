"""Requirement parsing, model failures, configuration and redaction tests."""

import pytest

from textile_foundry.config import Settings
from textile_foundry.exceptions import ConfigurationError, ModelOutputError, ModelTimeoutError
from textile_foundry.services.llm_service import (
    RuleBasedRequirementModel,
    StructuredRequirementModel,
)
from textile_foundry.utilities.redaction import redact


def test_rule_parser_extracts_requested_fields():
    parsed = RuleBasedRequirementModel().analyze(
        "开发夏季户外速干抗菌针织面料，成本控制在15元/米以内"
    )
    assert parsed.application == "summer_outdoor"
    assert parsed.fabric_category == "knitted"
    assert parsed.required_functions == ["quick_dry", "antibacterial"]
    assert parsed.target_cost is not None
    assert str(parsed.target_cost.amount) == "15"


def test_invalid_structured_json_is_bounded():
    class InvalidRunner:
        def invoke(self, prompt):
            return "{not-json"

    with pytest.raises(ModelOutputError):
        StructuredRequirementModel(InvalidRunner(), max_attempts=2).analyze("需求")


def test_timeout_is_bounded():
    class TimeoutRunner:
        def invoke(self, prompt):
            raise TimeoutError("network timeout")

    with pytest.raises(ModelTimeoutError):
        StructuredRequirementModel(TimeoutRunner(), max_attempts=2).analyze("需求")


def test_online_configuration_does_not_print_or_accept_missing_key():
    with pytest.raises(ConfigurationError):
        Settings(openai_model="model").require_online_configuration()


def test_redaction_removes_secret_values():
    output = redact("OPENAI_API_KEY=super-secret-token Authorization: Bearer-token")
    assert "super-secret-token" not in output
    assert "Bearer-token" not in output
    assert "[REDACTED]" in output
