"""Export the canonical baseline as a copyable LaTeX parameter table."""

import math
from pathlib import Path

import numpy as np

from src.config import load_config, validate_config


TABLE_PATH = Path(__file__).resolve().parents[1] / "report/sections/baseline_parameters.tex"


def number(value):
    text = format(float(value), ".12g")
    if "e" in text:
        mantissa, exponent = text.split("e")
        return mantissa + r"\times10^{" + str(int(exponent)) + "}"
    return text


def vector(values):
    return r"\left(" + ",".join(number(x) for x in values) + r"\right)^T"


def render_parameters(document):
    case = validate_config(document)
    p = case["physical"]
    orbit, magnetic, control = p["orbit"], p["magnetic"], p["controller"]
    initial, study = case["initial_conditions"], case["study"]
    inertia = r"\begin{pmatrix}" + r"\\".join(
        "&".join(number(x) for x in row) for row in p["inertia_kg_m2"]
    ) + r"\end{pmatrix}"
    rows = [
        ("Body inertia", "J", inertia + r"\ \mathrm{kg\,m^2}"),
        ("Initial attitude", "q_0", vector(initial["quaternion"])),
        ("Initial body rate", r"\omega(0)", vector(initial["angular_velocity_rad_s"]) + r"\ \mathrm{rad/s}"),
        ("Orbit altitude", "h_o", number(orbit["altitude_m"] / 1000) + r"\ \mathrm{km}"),
        ("Orbit inclination", "i", number(math.degrees(orbit["inclination_rad"])) + r"^\circ"),
        ("Ascending node and phase", r"\Omega,\phi", number(orbit["raan_rad"]) + "," + number(orbit["phase_rad"]) + r"\ \mathrm{rad}"),
        ("Initial spin magnitude", r"\omega_0", number(math.degrees(np.linalg.norm(initial["angular_velocity_rad_s"]))) + r"\ {}^\circ/\mathrm{s}"),
        ("Dipole limit", r"m_{\max}", number(control["max_dipole_a_m2"]) + r"\ \mathrm{A\,m^2}"),
        ("Normalized controller gain", "k_B", number(control["gain_kg_m2_s"]) + r"\ \mathrm{kg\,m^2/s}"),
        ("Earth radius", "R_E", number(orbit["earth_radius_m"]) + r"\ \mathrm{m}"),
        ("Gravity parameter", r"\mu", number(orbit["gravitational_parameter_m3_s2"]) + r"\ \mathrm{m^3/s^2}"),
        ("Earth rotation rate", r"\omega_E", number(magnetic["earth_rotation_rate_rad_s"]) + r"\ \mathrm{rad/s}"),
        ("Dipole tilt and phase", r"\alpha,\theta_0", number(math.degrees(magnetic["dipole_tilt_rad"])) + r"^\circ," + number(magnetic["earth_rotation_phase_rad"]) + r"\ \mathrm{rad}"),
        ("Equatorial field scale", r"B_{\rm eq}", number(magnetic["equatorial_surface_field_t"]) + r"\ \mathrm{T}"),
        ("Rate threshold", r"\omega_{\rm tol}", number(math.degrees(study["rate_threshold_rad_s"])) + r"\ {}^\circ/\mathrm{s}"),
        ("Required hold duration", r"T_{\rm hold}", number(study["hold_duration_s"]) + r"\ \mathrm{s}"),
        ("Mission deadline", r"T_{\rm deadline}", number(study["deadline_orbits"]) + "T_o"),
    ]
    lines = [r"\begin{table}[htbp]", r"\centering", r"\small", r"\begin{tabular}{lll}",
             r"\hline", r"Quantity & Symbol & Proposed value\\", r"\hline"]
    for label, symbol, value in rows:
        lines.append(label + r" & \(" + symbol + r"\) & \(" + value + r"\)\\")
    lines += [r"\hline", r"\end{tabular}",
              r"\caption{Preliminary inputs generated from the canonical baseline configuration. Values are study assumptions rather than measured hardware specifications.}",
              r"\label{tab_premise_inputs}", r"\end{table}"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    TABLE_PATH.write_text(render_parameters(load_config()), encoding="utf8")
    print("Exported report/sections/baseline_parameters.tex")
