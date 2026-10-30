"""Validated SI case inputs, separate from runtime callbacks and solver settings.

The canonical baseline is configs/baseline.json. Loading never silently
changes an initial quaternion or chooses an unverified integration step.
Runtime callback dictionaries use the contract in docs/dynamics_interface.md.
"""

import argparse
from copy import deepcopy
import json
import math
from pathlib import Path

import numpy as np

from ..physics.quaternion import normalize
from ..numerics.algebra import real_array, positive_definite_matrix


BASELINE = Path(__file__).resolve().parents[2] / "configs" / "baseline.json"
SCHEMA = {
    "physical": {
        "inertia_kg_m2": None,
        "orbit": dict.fromkeys(("earth_radius_m", "gravitational_parameter_m3_s2",
                               "altitude_m", "inclination_rad", "raan_rad", "phase_rad")),
        "magnetic": dict.fromkeys(("equatorial_surface_field_t", "dipole_tilt_rad",
                                  "earth_rotation_rate_rad_s", "earth_rotation_phase_rad")),
        "controller": dict.fromkeys(("law", "gain_kg_m2_s", "max_dipole_a_m2", "saturation")),
    },
    "initial_conditions": dict.fromkeys(("quaternion", "angular_velocity_rad_s")),
    "study": dict.fromkeys(("rate_threshold_rad_s", "hold_duration_s", "deadline_orbits")),
    "solver": dict.fromkeys(("method", "step_size_s")),
}


def _structure(value, schema, path):
    if not isinstance(value, dict) or set(value) != set(schema):
        raise ValueError(f"{path} must have exactly the documented keys {sorted(schema)}")
    paths = set()
    for key, child in schema.items():
        name = f"{path}.{key}" if path else key
        if child is None:
            paths.add(name)
        else:
            paths.update(_structure(value[key], child, name))
    return paths


def _scalar(value, name, positive=False, nonnegative=False):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ValueError(f"{name} must be a real numeric scalar")
    try:
        number = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    if positive and number <= 0:
        raise ValueError(f"{name} must be positive")
    if nonnegative and number < 0:
        raise ValueError(f"{name} must be nonnegative")
    return number


def _array(value, shape, name):
    return real_array(value, shape, name)


def _period(document):
    orbit = document["physical"]["orbit"]
    radius = orbit["earth_radius_m"] + orbit["altitude_m"]
    return 2 * math.pi * radius * math.sqrt(radius / orbit["gravitational_parameter_m3_s2"])


def validate_config(document):
    """Return an independent validated copy, or raise ValueError.

    Physical inputs are SI. The initial quaternion must already be unit to
    absolute component tolerance 1e-12. Numerical settings are kept in a
    separate section. Every parameter has a provenance entry.
    """
    root = dict(SCHEMA, schema_version=None, provenance=None)
    # Provenance is validated separately rather than treated as a parameter.
    paths = _structure(document, root, "") - {"schema_version", "provenance"}
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise ValueError("schema_version must be 1")
    result = deepcopy(document)
    physical = result["physical"]
    positive_definite_matrix(physical["inertia_kg_m2"], "inertia_kg_m2")
    orbit, magnetic, control = (physical[k] for k in ("orbit", "magnetic", "controller"))
    for key in ("earth_radius_m", "gravitational_parameter_m3_s2"):
        _scalar(orbit[key], key, positive=True)
    _scalar(orbit["altitude_m"], "altitude_m", nonnegative=True)
    for key in ("inclination_rad", "raan_rad", "phase_rad"):
        _scalar(orbit[key], key)
    if not 0 <= orbit["inclination_rad"] <= math.pi:
        raise ValueError("inclination_rad must be between zero and pi")
    _scalar(magnetic["equatorial_surface_field_t"], "equatorial_surface_field_t", positive=True)
    _scalar(magnetic["earth_rotation_rate_rad_s"], "earth_rotation_rate_rad_s", nonnegative=True)
    for key in ("dipole_tilt_rad", "earth_rotation_phase_rad"):
        _scalar(magnetic[key], key)
    if not 0 <= magnetic["dipole_tilt_rad"] <= math.pi:
        raise ValueError("dipole_tilt_rad must be between zero and pi")
    for key in ("gain_kg_m2_s", "max_dipole_a_m2"):
        _scalar(control[key], key, positive=True)
    if control["law"] != "normalized_b_dot" or control["saturation"] != "vector_norm":
        raise ValueError("controller must use normalized_b_dot and vector_norm saturation")
    initial = result["initial_conditions"]
    q = _array(initial["quaternion"], (4,), "quaternion")
    if not np.allclose(q, normalize(q), rtol=0, atol=1e-12):
        raise ValueError("initial quaternion must already have unit norm")
    _array(initial["angular_velocity_rad_s"], (3,), "angular_velocity_rad_s")
    for key, value in result["study"].items():
        _scalar(value, key, positive=True)
    solver = result["solver"]
    if solver["method"] != "rk4":
        raise ValueError("solver method must be rk4")
    if solver["step_size_s"] is not None:
        _scalar(solver["step_size_s"], "step_size_s", positive=True)
    try:
        period = _period(result)
        deadline = result["study"]["deadline_orbits"] * period
    except (ValueError, OverflowError, ZeroDivisionError) as exc:
        raise ValueError("derived orbit duration is invalid") from exc
    if not math.isfinite(period) or not math.isfinite(deadline) or period <= 0:
        raise ValueError("derived orbit duration must be finite and positive")
    if result["study"]["hold_duration_s"] > deadline:
        raise ValueError("hold_duration_s cannot exceed the mission deadline")
    provenance = result["provenance"]
    if not isinstance(provenance, dict) or set(provenance) != paths:
        raise ValueError("provenance must cover exactly every parameter path")
    for name, entry in provenance.items():
        if not isinstance(entry, dict) or set(entry) != {"classification", "note"}:
            raise ValueError(f"provenance for {name} must have classification and note")
        if not isinstance(entry["classification"], str) or entry["classification"] not in {"assumed", "derived", "project_choice", "pending"}:
            raise ValueError(f"invalid provenance classification for {name}")
        if not isinstance(entry["note"], str) or not entry["note"].strip():
            raise ValueError(f"provenance note for {name} must be nonempty")
    return result


def load_config(path=BASELINE):
    """Load and validate a case file using UTF8 JSON."""
    with Path(path).open(encoding="utf8") as stream:
        return validate_config(json.load(stream))


def initial_state(document):
    """Return a fresh seven component initial state without implicit projection."""
    initial = validate_config(document)["initial_conditions"]
    return np.r_[initial["quaternion"], initial["angular_velocity_rad_s"]]


def case_summary(document):
    """Return serializable derived timings and initialization for a recorded case."""
    document = validate_config(document)
    period = _period(document)
    return {"orbital_period_s": period,
            "deadline_s": document["study"]["deadline_orbits"] * period,
            "hold_duration_s": document["study"]["hold_duration_s"],
            "rate_threshold_rad_s": document["study"]["rate_threshold_rad_s"],
            "initial_state": initial_state(document).tolist(),
            "step_size_s": document["solver"]["step_size_s"]}


def solver_settings(document, require_step=False):
    """Return solver inputs separately; reject an unset step when requested."""
    solver = validate_config(document)["solver"]
    if require_step and solver["step_size_s"] is None:
        raise ValueError("step_size_s requires a completed convergence and metric refinement study")
    return solver


def runtime_config(document, *, field_model, controller):
    """Bind explicit callbacks to a fresh physical config suitable for rhs.

    Runtime keys are inertia, orbit, magnetic, controller_settings,
    field_model, and controller. Solver and study settings are not mixed
    into the physics. No production callback is supplied by this module.
    """
    if not callable(field_model) or not callable(controller):
        raise ValueError("field_model and controller must be callable")
    physical = validate_config(document)["physical"]
    return {"inertia": np.array(physical["inertia_kg_m2"], dtype=float),
            "orbit": physical["orbit"], "magnetic": physical["magnetic"],
            "controller_settings": physical["controller"],
            "field_model": field_model, "controller": controller}


def main():
    parser = argparse.ArgumentParser(description="Validate case inputs and print their summary")
    parser.add_argument("--config", type=Path, default=BASELINE)
    arguments = parser.parse_args()
    print(json.dumps(case_summary(load_config(arguments.config)), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
