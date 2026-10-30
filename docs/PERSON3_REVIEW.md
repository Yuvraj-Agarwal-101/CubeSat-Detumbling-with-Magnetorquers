# Person 3 merged field and control review

Sidhant's technical review contribution, executed with Codex assistance on
2026-10-30 on `codex/person3-field-control-review`, starting at `a8ceb29`.
Parent integration branch is `sidhant-final-integration`. No push, pilot,
engineering sweep, or new production timestep selection was performed.

## Attribution and scope

Reviewed the integration decisions, available Yuvraj handoff
(`docs/person2_handoff.md`; no separate Person 3 or YUVRAJ_HANDOFF file exists),
field/controller and dynamics contracts, numerical design/interfaces, Person 4
handoff, baseline, production and numerical implementations, existing tests,
verification scripts, evidence provenance, and report sections. The original
implementation record attributes field/controller implementation to work at
Aleksandar's request. Sidhant's contribution here is independent review,
additional verification, and documentation, not authorship of that existing code.
Student understanding and final contribution percentages are not certified by
this AI-assisted execution record.

## Independently checked equations and interfaces

With R = R_E + altitude and n = sqrt(mu/R^3), position is
R R3(RAAN) R1(i) [cos(nt+phase), sin(nt+phase), 0]. Its derivative is
R n R3(RAAN) R1(i) [-sin(nt+phase), cos(nt+phase), 0], in m/s.
The radius is 6,871,000 m and baseline period is 5668.144369061165 s.
Angles are radians, rotations are active and right handed, and phases have no
calendar epoch. Orbit closure is checked separately from magnetic periodicity.
A rotating tilted dipole generally does not repeat after one orbital period.

The unit axis d rotates about inertial z with d_dot = omega_E (e3 cross d).
For u = r/R, u_dot = v/R, b0 = B_eq (R_E/R)^3, and g = d dot u,

    B_I = b0 (3 g u - d)
    B_I_dot = b0 [3 (d_dot dot u + d dot u_dot) u + 3 g u_dot - d_dot].

Both orbital and Earth rotation contributions occur once; b0 is constant on
this circular orbit. Geometry gives equatorial magnitude b0, polar magnitude
2 b0, and inverse-cube radius scaling.

Scalar-first Hamilton quaternions and passive inertial-to-body C_BI are retained.
For positive z quarter-turn, inertial x maps to negative body y. The physical
RHS in `src/physics/dynamics.py` computes B_B = C_BI B_I and
B_B_dot = C_BI B_I_dot - omega cross B_B. Only this layer adds the body-rotation
correction; the controller consumes the supplied total body derivative unchanged.
`team_adapter.diagnostics` independently assembles the same diagnostic quantity,
without feeding a second correction into the RHS.

The normalized law is m_raw = -k_B B_B_dot / (B_B dot B_B), with k_B in
kg m^2/s, m in A m^2, and torque m cross B_B in N m. Zero derivative produces
zero command; zero field is explicitly rejected. Saturation scales the whole
vector by min(1, m_max/||m_raw||), retaining direction and the norm bound.
The exact boundary is unsaturated. No component clipping or hidden state occurs.

For a static inertial field, m_raw = k_B (omega cross B_B)/||B_B||^2.
Using (omega cross B) cross B = B (omega dot B) - omega ||B||^2 gives
tau = -k_B (I - b b^T) omega, where b is the unit body field. Constant symmetric
inertia and Euler's equation give

    E_dot = omega dot tau = -k_B ||omega - b (b dot omega)||^2.

The gyroscopic term contributes no power. Norm saturation multiplies this by
a nonnegative factor at most one. In the general orbital/rotating field case,
the extra torque -k_B [(C_BI B_I_dot) cross B_B]/||B_B||^2 has power of either
sign, so general monotonic rotational energy is not asserted.

The complete seven-component RHS was independently assembled at nine combinations
of time, attitude, and rate, including zero rate and a nonunit stage quaternion.
Its body field derivative was also checked by differentiating the independently
expanded passive matrix. The real adapter was instrumented at the controller
boundary: all four scratch RK4 stages use their own time and predicted state,
including a shortened last step. The time-first wrapper delegates to
`src/numerics/integrators.py`; projection occurs after the completed step.
No external time integrator was used.

## Findings and exact changes

No production orbit, field, controller, quaternion, dynamics, or adapter bug was
found, and none of those implementations was changed. Added 21 independent
checks in `tests/test_person3_review.py`, complementing the existing invalid-field,
known attitude, polar/equatorial, zero command, and saturation tests. New checks
cover inverse-cube scaling, axis rotation, orbit velocity/period versus magnetic
period, nonzero phases and refined derivatives at three Earth rotation rates,
oblique below/at/above saturation, input purity and repeatability, full RHS
assembly, body derivative sign, actual adapter stages, and static power including
parallel and zero rates.

The existing physics script now records normalized-LF SHA256 source hashes for
the actual merged physics, quaternion, adapter, both numerical layers, and itself.
The regenerated JSON and LaTeX preserve measured results. The report generator
now includes the static-field derivation, units, general-field limitation, and
the distinction between this review and timestep acceptance. Corrected the stale
claim that Person 4's pipeline was unmerged and updated the field conventions
section. Historical implementation records retain their original attribution.

## Executed checks and observed evidence

Commands run from repository root with the existing Windows virtual environment:

    .venv/Scripts/python.exe -m pytest -q tests/test_person3_review.py
    .venv/Scripts/python.exe -m studies.physics_verification
    .venv/Scripts/python.exe -m studies.verification
    .venv/Scripts/python.exe -m studies.lecture_validation
    .venv/Scripts/python.exe -m src.config
    .venv/Scripts/python.exe -m pytest -q
    git diff --check

The targeted suite passed 21 tests. The complete suite passed **305 tests**.
The physics script was rerun after its provenance/report changes. Centered
difference errors at h = 2, 1, 0.5 s decrease by approximately four on each
halving at t = 0, 123, 3456 s. Error ranges are 2.14779e-13 to 2.20238e-13,
5.36947e-14 to 5.50595e-14, and 1.34237e-14 to 1.37649e-14 T/s respectively.
Static measured/expected powers are -3.714285714285715e-7 /
-3.714285714285716e-7 W (unsaturated) and -7.211102550927979e-9 /
-7.211102550927981e-9 W (saturated).

The existing exact-solution numerical script measured fitted orders
1.0266708627 (Euler), 2.0498469098 (Heun), 4.0540021665 (scalar RK4), and
3.9994608948 (spherical rotation). Lecture truncation/stability examples also
completed successfully. These are numerical special cases, not detumbling
engineering results. Incidental regenerated numerical figures and rounding-only
table changes were restored to keep this contribution focused; fresh physical
evidence is retained in `data/processed/physics_verification.json`.

## Acceptance and next production-step task

Field/control equations and merged callback wiring are accepted by these automated
checks for use as the stated idealized continuous model in subsequent production
verification. This is not timestep approval, hardware validation, gain tuning,
or a recovery guarantee. Inputs remain assumed, with no noise, disturbances,
actuator dynamics, detailed geomagnetic model, or orbital perturbations.

Normalized-LF hash comparison against `production_validation/acceptance.json`
confirms the live field, controller, and adapter match the historical source.
Live `src/dynamics.py` and `src/integrators.py` do not. Historical acceptance is
from `7f0a3de`, with archived sources under `docs/integration_sources/aleksandar`.
Therefore the historical 1 s timestep **must be rerun on this merged revision**.
Passing instantaneous and short-horizon tests does not transfer that evidence.
No historical acceptance hashes or baseline solver settings were relabeled.

Before the 108-case pilot, the production-step task must:

1. Regenerate smooth and saturated six-orbit step refinements (including two
   successive passing comparisons), rather than reuse archived coarser runs.
2. Rerun quarter-second confirmation/output-grid audits of hold detection,
   saturation crossings, and peak resolution, and baseline 0.1 A m^2 stage-bound
   confirmation. Existing commands are `studies.timestep_selection`,
   `studies.complete_verification`, and `studies.baseline_confirmation`.
3. Ensure evidence hashes cover `src/physics/dynamics.py`,
   `src/physics/quaternion.py`, and `src/numerics/integrators.py`, not merely
   compatibility wrappers. Current historical hash guards must remain effective;
   fresh coarse evidence must precede confirmation and acceptance.
4. Review larger gains, rates, geometries, saturation transitions, local numerical
   stability, and output resolution relevant to the planned grid.
5. Obtain team confirmation of assumed baseline inputs, record the tested clean
   commit and evidence digests in the Person 4 verification gate, and complete
   the required review before running the pilot. Pilot runtime/accuracy review
   then precedes the larger engineering sweep. No engineering result is claimed.
