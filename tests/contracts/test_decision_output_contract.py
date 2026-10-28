"""E0.1 contract checks and an offline, deliberately limited schema interpreter.

This is NOT a general JSON Schema implementation. It supports only the keywords
listed in SUPPORTED_KEYWORDS, rejects all others before validating data, resolves
only local #/$defs/ references, and implements only the date-time format. It adds
explicit E0.1 cross-record invariants after structural validation. No dependencies,
network access, market logic, model, risk calculation or execution are involved.

Run standalone: python tests/contracts/test_decision_output_contract.py
Run tests: uv run pytest tests/contracts/test_decision_output_contract.py
"""

from __future__ import annotations

import copy
import json
import re
import sys
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import TypeAlias, cast

JSON: TypeAlias = "bool | int | float | str | list[JSON] | dict[str, JSON] | None"
JSONObject: TypeAlias = dict[str, JSON]

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas/decision-output-v0.1.schema.json"
FIXTURE_PATH = ROOT / "prototype/fixtures/decision-demo.json"
SUPPORTED_KEYWORDS = frozenset(
    {
        "$schema",
        "$id",
        "$defs",
        "$ref",
        "title",
        "description",
        "type",
        "const",
        "enum",
        "required",
        "properties",
        "additionalProperties",
        "minLength",
        "pattern",
        "format",
        "items",
        "minItems",
        "maxItems",
        "uniqueItems",
    }
)


class ContractError(ValueError):
    """The fixture or this interpreter's explicitly limited contract is invalid."""


def _object(value: JSON, path: str) -> JSONObject:
    if not isinstance(value, dict):
        raise ContractError(f"{path}: expected object")
    return value


def _array(value: JSON, path: str) -> list[JSON]:
    if not isinstance(value, list):
        raise ContractError(f"{path}: expected array")
    return value


def _string(value: JSON, path: str) -> str:
    if not isinstance(value, str):
        raise ContractError(f"{path}: expected string")
    return value


def _load(path: Path) -> JSONObject:
    return _object(cast(JSON, json.loads(path.read_text(encoding="utf-8"))), str(path))


def _same_json(left: JSON, right: JSON) -> bool:
    # Python otherwise treats True == 1 and False == 0.
    if isinstance(left, bool) != isinstance(right, bool):
        return False
    return left == right


def _check_schema(schema: JSONObject, path: str = "$schema") -> None:
    unsupported = set(schema) - SUPPORTED_KEYWORDS
    if unsupported:
        raise ContractError(f"{path}: unsupported schema keywords: {sorted(unsupported)}")
    for keyword in ("properties", "$defs"):
        if keyword in schema:
            for key, value in _object(schema[keyword], path).items():
                _check_schema(_object(value, f"{path}.{key}"), f"{path}.{keyword}.{key}")
    if "items" in schema:
        _check_schema(_object(schema["items"], path), f"{path}.items")
    if "type" in schema and schema["type"] not in {
        "object",
        "array",
        "string",
        "integer",
        "number",
        "boolean",
        "null",
    }:
        raise ContractError(f"{path}: unsupported type declaration")
    if "format" in schema and schema["format"] != "date-time":
        raise ContractError(f"{path}: unsupported format")
    if "additionalProperties" in schema and schema["additionalProperties"] is not False:
        raise ContractError(f"{path}: only additionalProperties=false is supported")
    if "$ref" in schema:
        reference = _string(schema["$ref"], path)
        if not reference.startswith("#/$defs/") or "/" in reference.removeprefix("#/$defs/"):
            raise ContractError(f"{path}: only a direct local #/$defs/ reference is supported")


def _validate(data: JSON, schema: JSONObject, root: JSONObject, path: str) -> None:
    if "$ref" in schema:
        name = _string(schema["$ref"], path).removeprefix("#/$defs/")
        definitions = _object(root.get("$defs"), "$schema.$defs")
        if name not in definitions:
            raise ContractError(f"{path}: unresolved local reference {name}")
        _validate(data, _object(definitions[name], path), root, path)
    kind = schema.get("type")
    matches = {
        "object": isinstance(data, dict),
        "array": isinstance(data, list),
        "string": isinstance(data, str),
        "integer": isinstance(data, int) and not isinstance(data, bool),
        "number": isinstance(data, int | float) and not isinstance(data, bool),
        "boolean": isinstance(data, bool),
        "null": data is None,
    }
    if kind is not None and not matches[_string(kind, path)]:
        raise ContractError(f"{path}: expected {kind}")
    if "const" in schema and not _same_json(data, schema["const"]):
        raise ContractError(f"{path}: const mismatch")
    if "enum" in schema and not any(
        _same_json(data, option) for option in _array(schema["enum"], path)
    ):
        raise ContractError(f"{path}: invalid enum")
    if isinstance(data, dict):
        properties = _object(schema.get("properties", {}), path)
        for required in _array(schema.get("required", []), path):
            key = _string(required, path)
            if key not in data:
                raise ContractError(f"{path}.{key}: required field missing")
        if schema.get("additionalProperties") is False:
            extra = set(data) - set(properties)
            if extra:
                raise ContractError(f"{path}: additional fields: {sorted(extra)}")
        for key, value in data.items():
            if key in properties:
                _validate(value, _object(properties[key], path), root, f"{path}.{key}")
    if isinstance(data, list):
        for keyword in ("minItems", "maxItems"):
            if keyword in schema:
                limit = schema[keyword]
                if not isinstance(limit, int) or isinstance(limit, bool):
                    raise ContractError(f"{path}: invalid schema {keyword}")
                if (keyword == "minItems" and len(data) < limit) or (
                    keyword == "maxItems" and len(data) > limit
                ):
                    raise ContractError(f"{path}: {keyword} violated")
        if schema.get("uniqueItems") is True:
            serialized = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in data]
            if len(serialized) != len(set(serialized)):
                raise ContractError(f"{path}: duplicate array items")
        if "items" in schema:
            for index, item in enumerate(data):
                _validate(item, _object(schema["items"], path), root, f"{path}[{index}]")
    if isinstance(data, str):
        if "minLength" in schema:
            minimum = schema["minLength"]
            if not isinstance(minimum, int) or isinstance(minimum, bool):
                raise ContractError(f"{path}: invalid schema minLength")
            if len(data) < minimum:
                raise ContractError(f"{path}: minLength violated")
        if "pattern" in schema and re.search(_string(schema["pattern"], path), data) is None:
            raise ContractError(f"{path}: pattern mismatch")
        if schema.get("format") == "date-time":
            try:
                parsed = datetime.fromisoformat(data.replace("Z", "+00:00"))
            except ValueError as error:
                raise ContractError(f"{path}: invalid date-time") from error
            if "T" not in data or parsed.tzinfo is None:
                raise ContractError(f"{path}: date-time requires T and explicit timezone")


def _records(document: JSONObject, key: str) -> list[JSONObject]:
    return [_object(item, key) for item in _array(document[key], key)]


def _invariants(document: JSONObject) -> None:
    candidates = _records(document, "candidates")
    scenarios = _records(document, "scenarios")
    candidate_ids = [_string(item["id"], "candidate.id") for item in candidates]
    scenario_ids = [_string(item["id"], "scenario.id") for item in scenarios]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ContractError("candidates: duplicate IDs")
    if len(scenario_ids) != len(set(scenario_ids)):
        raise ContractError("scenarios: duplicate IDs")
    display = _object(document["display"], "display")
    if display["default_scenario"] not in scenario_ids:
        raise ContractError("display.default_scenario: missing scenario")
    referenced: set[str] = set()
    snapshot = _object(document["snapshot"], "snapshot")
    for candidate in candidates:
        if candidate["id"] != candidate["code"]:
            raise ContractError("candidate: id and fictional code must match")
        audit = _object(candidate["audit"], "audit")
        if audit["snapshot_id"] != snapshot["id"]:
            raise ContractError("audit.snapshot_id: inconsistent snapshot")
        if candidate["action"] == "NO_TRADE" and candidate["block_reason"] == "NONE":
            raise ContractError("candidate.NO_TRADE: explicit block reason required")
        if candidate["action"] in {"HOLD", "REDUCE", "EXIT"}:
            gate = _object(candidate["risk_gate"], "risk_gate")
            if gate["risk_reduction_allowed"] is not True:
                raise ContractError("candidate: lawful risk-reduction semantics lost")
    by_id = dict(zip(candidate_ids, candidates, strict=True))
    for scenario in scenarios:
        for raw_id in _array(scenario["candidate_ids"], "scenario.candidate_ids"):
            candidate_id = _string(raw_id, "scenario.candidate_ids")
            if candidate_id not in by_id:
                raise ContractError("scenario.candidate_ids: unknown candidate reference")
            referenced.add(candidate_id)
            if scenario["market_posture"] == "NO_NEW_RISK":
                gate = _object(by_id[candidate_id]["risk_gate"], "risk_gate")
                if (
                    scenario["new_risk_allowed"] is not False
                    or gate["new_risk_allowed"] is not False
                ):
                    raise ContractError("NO_NEW_RISK: new risk must stay blocked")
    if referenced != set(candidate_ids):
        raise ContractError("candidates: unreferenced record")


def validate_contract(document: JSON, schema: JSONObject | None = None) -> None:
    """Validate the exact E0.1 subset and cross-record invariants, without any I/O beyond schema."""
    resolved_schema = _load(SCHEMA_PATH) if schema is None else schema
    _check_schema(resolved_schema)
    _validate(document, resolved_schema, resolved_schema, "$")
    _invariants(_object(document, "$"))


def _fixture() -> JSONObject:
    return _load(FIXTURE_PATH)


def _candidate(document: JSONObject, index: int = 0) -> JSONObject:
    return _records(document, "candidates")[index]


def _reject(document: JSON, expected: str = "") -> None:
    try:
        validate_contract(document)
    except ContractError as error:
        assert expected in str(error), str(error)
    else:
        raise AssertionError("Invalid fixture was accepted")


def _nested_objects(document: JSON) -> Iterator[JSONObject]:
    if isinstance(document, dict):
        yield document
        for item in document.values():
            yield from _nested_objects(item)
    elif isinstance(document, list):
        for item in document:
            yield from _nested_objects(item)


def test_authored_fixture_passes_offline_contract() -> None:
    validate_contract(_fixture())


def test_required_summary_fields_cannot_disappear() -> None:
    for field in _fixture():
        document = _fixture()
        del document[field]
        _reject(document, "required field missing")
    for field in _candidate(_fixture()):
        document = _fixture()
        del _candidate(document)[field]
        _reject(document, "required field missing")


def test_required_evidence_detail_and_audit_fields_cannot_disappear() -> None:
    for section in ("evidence", "execution", "details", "audit"):
        for field in _object(_candidate(_fixture())[section], section):
            document = _fixture()
            del _object(_candidate(document)[section], section)[field]
            _reject(document, "required field missing")


def test_unknown_values_are_null_and_carry_nonempty_reasons() -> None:
    document = _fixture()
    unknowns = [
        item
        for item in _nested_objects(document)
        if item.get("status") == "UNKNOWN" and "value" in item
    ]
    assert unknowns
    assert all(item["value"] is None and item["reason"] for item in unknowns)
    for field, value in (("value", ""), ("value", 0), ("reason", ""), ("reason", "   ")):
        document = _fixture()
        unknown = _object(_candidate(document)["earliest_execution"], "earliest_execution")
        unknown[field] = value
        _reject(document)


def test_unknown_does_not_become_silent_omission() -> None:
    document = _fixture()
    unknown = _object(_candidate(document)["reference_price_area"], "reference_price_area")
    del unknown["reason"]
    _reject(document, "required field missing")


def test_invalid_action_block_and_posture_enums_rejected() -> None:
    for field in ("action", "block_reason"):
        document = _fixture()
        _candidate(document)[field] = "BUY_NOW"
        _reject(document, "invalid enum")
    document = _fixture()
    _records(document, "scenarios")[0]["market_posture"] = "BULL_CERTAIN"
    _reject(document, "invalid enum")


def test_wrong_types_and_boolean_number_confusion_rejected() -> None:
    for field, value in (("code", 123456), ("evidence", []), ("trigger_or_wait", False)):
        document = _fixture()
        _candidate(document)[field] = value
        _reject(document, "expected")
    document = _fixture()
    _object(document["display"], "display")["max_candidates"] = True
    _reject(document, "const mismatch")


def test_no_new_risk_retains_hold_reduce_exit_without_execution_permission() -> None:
    document = _fixture()
    scenario = next(
        item for item in _records(document, "scenarios") if item["market_posture"] == "NO_NEW_RISK"
    )
    by_id = {_string(item["id"], "id"): item for item in _records(document, "candidates")}
    actions = {
        _string(by_id[_string(cid, "id")]["action"], "action")
        for cid in _array(scenario["candidate_ids"], "candidate_ids")
    }
    assert actions == {"HOLD", "REDUCE", "EXIT"}
    assert scenario["new_risk_allowed"] is False
    assert scenario["risk_reduction_allowed"] is True
    authorization = _object(document["authorization"], "authorization")
    assert authorization["trading_authorized"] is False
    validate_contract(document)


def test_no_new_risk_cannot_enable_new_risk_or_force_disable_lawful_reduction() -> None:
    for field, value in (("new_risk_allowed", True), ("risk_reduction_allowed", False)):
        document = _fixture()
        _records(document, "scenarios")[1][field] = value
        _reject(document, "const mismatch")
    document = _fixture()
    gate = _object(_candidate(document, 4)["risk_gate"], "risk_gate")
    gate["new_risk_allowed"] = True
    _reject(document, "const mismatch")


def test_no_trade_requires_an_explicit_block_reason() -> None:
    document = _fixture()
    _candidate(document, 2)["block_reason"] = "NONE"
    _reject(document, "explicit block reason required")


def test_fixture_is_synthetic_at_root_and_every_record() -> None:
    document = _fixture()
    for item in [document, *_records(document, "candidates")]:
        assert item["data_classification"] == "SYNTHETIC_DEMO_DATA"
    document["data_classification"] = "LIVE"
    _reject(document, "const mismatch")
    document = _fixture()
    _candidate(document)["code"] = "600000"
    _reject(document, "pattern mismatch")
    document = _fixture()
    _candidate(document)["name"] = "真实证券名称"
    _reject(document, "pattern mismatch")


def test_default_and_all_switchable_scenarios_have_at_most_three_candidates() -> None:
    document = _fixture()
    assert _object(document["display"], "display")["max_candidates"] == 3
    assert all(
        len(_array(item["candidate_ids"], "ids")) <= 3 for item in _records(document, "scenarios")
    )
    _array(_records(document, "scenarios")[0]["candidate_ids"], "ids").append("SYN-GAMMA")
    _reject(document, "maxItems violated")


def test_unapproved_risk_values_remain_null_and_no_hidden_fields_exist() -> None:
    for value in (0, 0.1, "10%"):
        document = _fixture()
        pending = _object(_candidate(document)["maximum_candidate_position"], "position")
        pending["value"] = value
        _reject(document, "const mismatch")
    document = _fixture()
    _candidate(document)["stop_loss"] = 0.05
    _reject(document, "additional fields")


def test_authorization_cannot_expand_scope_and_data_4_1_stays_paused() -> None:
    fixture_authorization = _object(_fixture()["authorization"], "authorization")
    prohibited = [field for field in fixture_authorization if field.endswith("_authorized")]
    assert prohibited
    for field in prohibited:
        document = _fixture()
        _object(document["authorization"], "authorization")[field] = True
        _reject(document, "const mismatch")
    for field, value in (
        ("id", "AUTH-ENG-0001"),
        ("data_4_1", "ACTIVE"),
        ("read_only", False),
        ("expires_at", "2099-01-01T00:00:00Z"),
        ("content_hash", "unverified"),
        ("engineering_scope", "DATA-4.1"),
    ):
        document = _fixture()
        _object(document["authorization"], "authorization")[field] = value
        _reject(document, "const mismatch")


def test_fixture_contains_all_authorized_state_examples() -> None:
    document = _fixture()
    candidates = _records(document, "candidates")
    postures = {
        _string(item["market_posture"], "posture") for item in _records(document, "scenarios")
    }
    assert {"SELECTIVE", "NO_NEW_RISK"} <= postures
    blocks = {_string(item["block_reason"], "block") for item in candidates}
    assert {"INSUFFICIENT_EVIDENCE", "CONFOUNDED", "WINDOW_CLOSED", "NON_EXECUTABLE"} <= blocks
    actions = {_string(item["action"], "action") for item in candidates}
    assert {"HOLD", "REDUCE", "EXIT"} <= actions


def test_references_duplicate_ids_and_orphans_are_rejected() -> None:
    document = _fixture()
    _array(_records(document, "scenarios")[0]["candidate_ids"], "ids")[0] = "SYN-MISSING"
    _reject(document, "unknown candidate reference")
    document = _fixture()
    _candidate(document, 1)["id"] = _candidate(document)["id"]
    _reject(document, "duplicate IDs")
    document = _fixture()
    _object(document["display"], "display")["default_scenario"] = "missing"
    _reject(document, "missing scenario")
    document = _fixture()
    orphan = copy.deepcopy(_candidate(document))
    orphan["id"] = "SYN-ORPHAN"
    orphan["code"] = "SYN-ORPHAN"
    _array(document["candidates"], "candidates").append(orphan)
    _reject(document, "unreferenced record")


def test_audit_snapshot_and_fictional_identity_cannot_drift() -> None:
    document = _fixture()
    _object(_candidate(document)["audit"], "audit")["snapshot_id"] = "SYN-OTHER"
    _reject(document, "inconsistent snapshot")
    document = _fixture()
    _candidate(document)["code"] = "SYN-OTHER"
    _reject(document, "id and fictional code must match")


def test_time_values_are_explicit_static_timezone_aware_snapshots() -> None:
    for value in ("2026-10-28", "2026-10-28T07:11:04", "yesterday"):
        document = _fixture()
        _object(document["snapshot"], "snapshot")["generated_at"] = value
        _reject(document, "date-time")
    document = _fixture()
    assert _object(document["snapshot"], "snapshot")["freshness"] == "STATIC_SYNTHETIC_SNAPSHOT"
    for item in _records(document, "candidates"):
        timeline = _object(_object(item["details"], "details")["information_timeline"], "timeline")
        assert _object(timeline["signal_generated_at"], "signal_generated_at")["value"] is None


def test_unimplemented_schema_assertions_fail_closed_even_in_unused_definitions() -> None:
    schema = _load(SCHEMA_PATH)
    _object(schema["$defs"], "$defs")["unused"] = {"minimum": 1}
    try:
        validate_contract(_fixture(), schema)
    except ContractError as error:
        assert "unsupported schema keywords" in str(error)
    else:
        raise AssertionError("Unsupported assertion keyword was silently ignored")


def test_external_schema_references_are_never_fetched() -> None:
    schema = _load(SCHEMA_PATH)
    schema["$ref"] = "https://example.invalid/schema.json"
    try:
        validate_contract(_fixture(), schema)
    except ContractError as error:
        assert "only a direct local" in str(error)
    else:
        raise AssertionError("External schema reference was accepted")


if __name__ == "__main__":
    try:
        validate_contract(_fixture())
    except (ContractError, OSError, json.JSONDecodeError) as error:
        sys.stderr.write(f"E0.1 contract validation failed: {error}\n")
        raise SystemExit(1) from error
    sys.stdout.write(
        "PASS: synthetic E0.1 fixture matches the supported contract and invariants.\n"
    )
