"""Exact IVP convergence, torque free invariants, and linear stability.

These numerical verification studies do not simulate magnetic detumbling.
All trajectories use the numerical methods implemented in this repository.
"""

import csv
import json
import os
import shutil
from pathlib import Path

import numpy as np

from src.numerics.errors import fit_order, quaternion_error, trajectory_norm
from src.numerics.integrators import integrate, rk4
from src.numerics.stability import amplification
from src.physics.dynamics import angular_acceleration
from src.physics.quaternion import normalize, quaternion_derivative, rotation_matrix
from src.physics.verification import exact_free_sphere, project_attitude


ROOT = Path(__file__).resolve().parents[1]


def free_body(inertia):
    def f(u, t):
        return np.r_[quaternion_derivative(u[:4], u[4:]),
                     angular_acceleration(u[4:], np.zeros(3), inertia)]
    return f


def convergence():
    records, orders = [], {}
    steps = .2 / 2 ** np.arange(5)
    for method in ("euler", "heun", "rk4"):
        errors = []
        for dt in steps:
            t, u, _ = integrate(lambda u, t: -u, [1.0], 2, dt, method=method)
            error = np.exp(-t) - u[:, 0]
            size = trajectory_norm(t, error)
            errors.append(size)
            records.append({"case": "scalar_decay", "method": method, "dt": float(dt),
                            "error_l2": float(size), "error_final": float(abs(error[-1]))})
        orders[method] = fit_order(steps, errors)[0]
    omega, q0 = np.array([.3, -.2, .4]), normalize([.7, .2, -.1, .3])
    q_errors = []
    for dt in .4 / 2 ** np.arange(5):
        t, u, _ = rk4(free_body(2 * np.eye(3)), np.r_[q0, omega], 4, dt, project=project_attitude)
        error = quaternion_error(exact_free_sphere(t, q0, omega), u[:, :4])
        size = trajectory_norm(t, error)
        q_errors.append(size)
        records.append({"case": "spherical_rotation", "method": "rk4", "dt": float(dt),
                        "error_l2": float(size), "error_final": float(error[-1])})
    orders["spherical_rotation"] = fit_order(.4 / 2 ** np.arange(5), q_errors)[0]
    return records, orders


def invariants():
    inertia = np.diag([.030, .035, .007])
    initial = np.r_[normalize([.7, .2, -.1, .3]), [.4, .3, .5]]
    records = []
    for dt in .4 / 2 ** np.arange(5):
        t, u, diagnostics = rk4(free_body(inertia), initial, 20, dt, project=project_attitude)
        energy = np.array([.5 * w @ inertia @ w for w in u[:, 4:]])
        momentum = np.array([rotation_matrix(state[:4]).T @ inertia @ state[4:] for state in u])
        records.append({"dt": float(dt),
                        "max_relative_energy_error": float(np.max(abs(energy - energy[0])) / energy[0]),
                        "max_relative_momentum_error": float(np.max(np.linalg.norm(momentum - momentum[0], axis=1)) / np.linalg.norm(momentum[0])),
                        "max_projection_correction": float(np.max(diagnostics["projection_correction_norm"]))})
    return records


def save_csv(path, records):
    with path.open("w", newline="", encoding="utf8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def main():
    output, figures = ROOT / "data/processed", ROOT / "figures"
    output.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    records, orders = convergence()
    conserved = invariants()
    stability = [{"dt_for_lambda_minus_one": dt, "rk4_amplification": float(amplification(-dt)),
                  "absolutely_stable": bool(abs(amplification(-dt)) < 1)} for dt in [.5, 1, 2, 2.7, 2.8, 3]]
    save_csv(output / "verification_convergence.csv", records)
    save_csv(output / "verification_invariants.csv", conserved)
    save_csv(output / "verification_stability.csv", stability)
    (output / "verification_summary.json").write_text(json.dumps({"orders": orders,
        "scope": "Exact IVP verification and torque free invariants only",
        "scalar_duration": 2, "scalar_steps": (.2 / 2 ** np.arange(5)).tolist(),
        "spherical_steps_s": (.4 / 2 ** np.arange(5)).tolist(),
        "initial_quaternion_before_normalization": [.7, .2, -.1, .3],
        "initial_rate_rad_s": [.3, -.2, .4], "spherical_duration_s": 4,
        "invariant_duration_s": 20, "invariant_inertia_kg_m2": [.030, .035, .007],
        "invariant_initial_rate_rad_s": [.4, .3, .5]}, indent=2) + "\n")

    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "report/build/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 4))
    for method, style, marker in [("euler", "-", "o"), ("heun", "--", "s"), ("rk4", ":", "^")]:
        selected = [row for row in records if row["case"] == "scalar_decay" and row["method"] == method]
        ax.loglog([x["dt"] for x in selected], [x["error_l2"] for x in selected],
                  color="black", linestyle=style, marker=marker, label=method.upper())
    ax.set(xlabel="Time step", ylabel="Time weighted error norm")
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures / "verification_convergence.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    for key, label, style in [("max_relative_energy_error", "Energy", "-o"),
                               ("max_relative_momentum_error", "Inertial momentum", "--s")]:
        ax.loglog([x["dt"] for x in conserved], [x[key] for x in conserved], style, color="black", label=label)
    ax.set(xlabel="Time step in seconds", ylabel="Maximum relative invariant error")
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures / "verification_invariants.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    w = np.linspace(-3.5, 0, 500)
    for method, style in [("euler", "-"), ("heun", "--"), ("rk4", ":")]:
        ax.plot(w, np.abs(amplification(w, method)), color="black", linestyle=style, label=method.upper())
    ax.axhline(1, color="0.5", linewidth=1)
    ax.set(xlabel="Time step times eigenvalue", ylabel="Amplification magnitude", ylim=(0, 2.5))
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures / "verification_stability.png", dpi=200)
    plt.close(fig)

    report_figures = ROOT / "report/figures"
    report_figures.mkdir(exist_ok=True)
    for name in ("verification_convergence.png", "verification_invariants.png", "verification_stability.png"):
        shutil.copyfile(figures / name, report_figures / name)

    lines = [r"\begin{tabular}{lr}", r"\hline", r"Problem and method & Fitted order\\", r"\hline"]
    for name, label in [("euler", "Scalar decay with Euler"), ("heun", "Scalar decay with Heun"),
                        ("rk4", "Scalar decay with RK4"), ("spherical_rotation", "Spherical rotation with RK4")]:
        lines.append(label + " & " + format(orders[name], ".4f") + r"\\")
    lines += [r"\hline", r"\end{tabular}"]
    (ROOT / "report/sections/verification_orders.tex").write_text("\n".join(lines) + "\n")
    print(json.dumps(orders, indent=2))


if __name__ == "__main__":
    main()
