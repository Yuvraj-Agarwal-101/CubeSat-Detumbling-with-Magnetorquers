"""Canonical inputs, validation, SI conversions, and dynamics binding."""

from copy import deepcopy
import json
import math

import numpy as np
import pytest
from numpy.testing import assert_allclose

from src.config import (case_summary, initial_state, load_config, runtime_config,
                        solver_settings, validate_config)
from src.dynamics import rhs


def change(case, path, value):
    parts = path.split(".")
    parent = case
    for key in parts[:-1]:
        parent = parent[key]
    parent[parts[-1]] = value
    return case


def test_baseline_matches_handoff_si_inputs():
    case = load_config()
    assert_allclose(case["physical"]["inertia_kg_m2"], np.diag([.03, .035, .007]))
    assert_allclose(case["physical"]["orbit"]["inclination_rad"], np.deg2rad(55))
    assert_allclose(case["physical"]["magnetic"]["dipole_tilt_rad"], np.deg2rad(11))
    y0 = initial_state(case)
    assert_allclose(y0[:4], [1, 0, 0, 0])
    assert_allclose(y0[4:], np.ones(3) * np.deg2rad(10) / np.sqrt(3))
    assert_allclose(case["study"]["rate_threshold_rad_s"], np.deg2rad(.5))
    assert solver_settings(case)["step_size_s"] is None


def test_period_and_deadline_against_kepler_circular_relation():
    case = load_config()
    expected_period = 2 * math.pi * math.sqrt(6871000 ** 3 / 3.986004418e14)
    summary = case_summary(case)
    assert_allclose(summary["orbital_period_s"], expected_period, rtol=1e-14)
    assert_allclose(summary["deadline_s"], 6 * expected_period, rtol=1e-14)
    assert summary["hold_duration_s"] == 600
    assert len(summary["initial_state"]) == 7
    json.dumps(summary, allow_nan=False)


def test_validation_and_export_preserve_independent_copies():
    case = load_config()
    before = deepcopy(case)
    copied = validate_config(case)
    copied["physical"]["orbit"]["altitude_m"] = 1
    state = initial_state(case)
    state[0] = 2
    numerical = solver_settings(case)
    numerical["step_size_s"] = 1
    assert case == before


def test_step_must_be_selected_explicitly():
    with pytest.raises(ValueError, match="convergence"):
        solver_settings(load_config(), require_step=True)
    case = change(load_config(), "solver.step_size_s", .1)
    assert solver_settings(case, require_step=True)["step_size_s"] == .1


@pytest.mark.parametrize("path, bad", [
    ("schema_version", 2), ("schema_version", True),
    ("physical.inertia_kg_m2", [[1, 0], [0, 1]]),
    ("physical.inertia_kg_m2", [[1, 0, 0], [0, 0, 0], [0, 0, 1]]),
    ("physical.inertia_kg_m2", [[1, 0, 0], [0, -1, 0], [0, 0, 1]]),
    ("physical.inertia_kg_m2", [[1, .1, 0], [0, 1, 0], [0, 0, 1]]),
    ("physical.orbit.earth_radius_m", 0),
    ("physical.orbit.gravitational_parameter_m3_s2", -1),
    ("physical.orbit.altitude_m", -1),
    ("physical.orbit.inclination_rad", 55),
    ("physical.orbit.phase_rad", float("nan")),
    ("physical.orbit.raan_rad", float("inf")),
    ("physical.orbit.altitude_m", True),
    ("physical.orbit.earth_radius_m", "6371000"),
    ("physical.magnetic.equatorial_surface_field_t", 0),
    ("physical.magnetic.dipole_tilt_rad", -1),
    ("physical.magnetic.earth_rotation_rate_rad_s", -1),
    ("physical.magnetic.earth_rotation_phase_rad", 1j),
    ("physical.controller.gain_kg_m2_s", 0),
    ("physical.controller.max_dipole_a_m2", -1),
    ("physical.controller.law", "unnormalized_b_dot"),
    ("physical.controller.saturation", "componentwise"),
    ("initial_conditions.quaternion", [2, 0, 0, 0]),
    ("initial_conditions.quaternion", [0, 0, 0, 0]),
    ("initial_conditions.quaternion", [1j, 0, 0, 0]),
    ("initial_conditions.angular_velocity_rad_s", [0, 0]),
    ("initial_conditions.angular_velocity_rad_s", [0, float("nan"), 0]),
    ("study.rate_threshold_rad_s", 0),
    ("study.hold_duration_s", -1),
    ("study.deadline_orbits", 0),
    ("study.hold_duration_s", 1e9),
    ("solver.method", "solve_ivp"),
    ("solver.step_size_s", 0),
    ("solver.step_size_s", float("inf")),
])
def test_invalid_case_parameters(path, bad):
    with pytest.raises(ValueError):
        validate_config(change(load_config(), path, bad))


def test_missing_and_unknown_keys_are_rejected():
    case = load_config()
    del case["physical"]["controller"]["gain_kg_m2_s"]
    with pytest.raises(ValueError, match="keys"):
        validate_config(case)
    case = load_config()
    case["physical"]["orbit"]["inclination_deg"] = 55
    with pytest.raises(ValueError, match="keys"):
        validate_config(case)


@pytest.mark.parametrize("bad", [None, {}, [], {"classification": "measured", "note": "test"},
                                  {"classification": "assumed", "note": ""}])
def test_invalid_parameter_provenance(bad):
    case = load_config()
    case["provenance"]["physical.inertia_kg_m2"] = bad
    with pytest.raises(ValueError, match="provenance"):
        validate_config(case)


def test_provenance_must_cover_exactly_the_case_parameters():
    case = load_config()
    del case["provenance"]["solver.step_size_s"]
    with pytest.raises(ValueError, match="provenance"):
        validate_config(case)
    case = load_config()
    case["provenance"]["extra"] = {"classification": "assumed", "note": "test"}
    with pytest.raises(ValueError, match="provenance"):
        validate_config(case)


def test_json_roundtrip_and_custom_path(tmp_path):
    case = load_config()
    path = tmp_path / "case.json"
    path.write_text(json.dumps(case), encoding="utf8")
    assert load_config(path) == case


def test_runtime_binding_matches_rhs_and_does_not_mix_solver_settings():
    # Explicit artificial fixtures, not a production field or controller.
    seen = []

    def field(t, runtime):
        seen.append(runtime["orbit"]["altitude_m"])
        return [0, 0, 3e-5], [0, 0, 0]

    def controller(t, q, omega, b, db, runtime):
        assert runtime["controller_settings"]["saturation"] == "vector_norm"
        return {"raw_dipole": [0, 0, 0], "dipole": [0, 0, 0],
                "torque": [0, 0, 0], "saturated": False}

    case = load_config()
    before = deepcopy(case)
    runtime = runtime_config(case, field_model=field, controller=controller)
    derivative = rhs(0, initial_state(case), runtime)
    assert derivative.shape == (7,)
    assert np.all(np.isfinite(derivative))
    assert seen == [500000]
    assert "solver" not in runtime and "study" not in runtime
    runtime["orbit"]["altitude_m"] = 1
    runtime["inertia"][0, 0] = 1
    assert case == before


@pytest.mark.parametrize("field, controller", [(None, lambda: None), (lambda: None, None)])
def test_runtime_binding_rejects_missing_callbacks(field, controller):
    with pytest.raises(ValueError, match="callable"):
        runtime_config(load_config(), field_model=field, controller=controller)


def test_full_symmetric_inertia_and_zero_initial_rate_are_valid():
    case = load_config()
    case["physical"]["inertia_kg_m2"] = [[.03, .001, 0], [.001, .035, 0], [0, 0, .007]]
    case["initial_conditions"]["angular_velocity_rad_s"] = [0, 0, 0]
    assert_allclose(initial_state(validate_config(case))[4:], 0)
