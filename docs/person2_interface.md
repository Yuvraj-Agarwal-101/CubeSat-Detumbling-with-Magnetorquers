# Person 2 integration and reproduction interface

Use the repository README for the tested environment and exact commands. This contribution follows the existing src, tests, studies, configs, data/processed, figures and report layout.

## RK4 contract

```python
from src.integrators import rk4
from src.dynamics import rhs
from src.quaternion import normalize
import numpy as np

def project(y):
    result = y.copy()
    result[:4] = normalize(result[:4])
    return result

result = rk4(lambda t, y: rhs(t, y, config), y0, (0.0, deadline), h,
             projection=project,
             norm_diagnostic=lambda y: np.linalg.norm(y[:4]))
```

The derivative is evaluated four times per completed step, at the actual stage time and state. The input quaternion must already have unit norm. Projection is applied only after completed steps. A shortened final step lands at the deadline.

1. result.times has shape (N,).
2. result.states has shape (N, 7) for spacecraft states.
3. result.preprojection_norm_error has shape (N,). Index zero is the supplied initial norm minus one. Later entries are recorded before correction. Without a diagnostic callback the array contains NaN.
4. result.function_evaluations equals 4*(N-1).

The time first public solver delegates to the common numerical layer in src/numerics/integrators.py. Its signature, result object, and signed diagnostics remain unchanged. The generic solver contains no spacecraft physics and does not build attitude matrices. The shared dynamics evaluates a matrix from a normalized local copy of each stage quaternion while retaining the unprojected quaternion for its derivative. Tests verify fresh field/controller calls at all four stages.

## Production adapter

Read studies/adapter_template.py for the full case dictionary. Runtime config contains inertia, field_model and controller callbacks. config_record is the complete validated canonical case document from src.config. callback_identifiers separately records the field and controller import paths. The runtime configuration comes from src.config.runtime_config, and the dipole limit is controller_settings[max_dipole_a_m2]. Do not attempt to serialize Python functions. The diagnostics callback returns raw_dipole, dipole and torque using the same shared controller as rhs. Each is a three component vector.

Supply at least one real unsaturated and one real saturated case, normalized initial attitude, explicit seed or null, six orbital periods, and a description of stage matrix handling. Fixtures cannot be labeled as production models.

The screening metrics use stored endpoints. Detumbling start is the first sampled start of an uninterrupted sampled interval lasting at least 600 seconds at or below the threshold. This approximates the required earliest continuous start and can miss excursions between samples. Saturation fraction uses trapezoidal time weighting of the Boolean condition. Peak torque is a sampled maximum. Dipole effort is actuator activity, not electrical energy.

The proposed tolerance gate requires two consecutive successful comparisons for every case and at least one successful case. Relative tolerances are one percent for time, final rate and peak torque. Absolute floors are 1 second, 1e-6 rad/s and 1e-10 N m. Saturation fraction uses absolute 0.005. The full model and event resolution must be reviewed before using a selected candidate for production sweeps.

## Supplied evidence and remaining work

There are 20 independent Person 2 unit tests and three shared dynamics integration checks. The merged suite contains 222 tests. Convergence data and six step sizes for each additional exact problem are stored with complete inputs. The source extraction is docs/person2_source_extracted.txt and the structured handoff is docs/person2_handoff.md. Copyable LaTeX is in report/PERSON2_FRAGMENTS.md. The generator writes sections/person2_verification.tex separately from sections/numerical_verification.tex.

Production field/control, a justified production step, real smooth and saturated refinement studies, engineering sweeps, final contribution percentages and independent teammate reproduction remain pending. The repository exists on GitHub; this document makes no claim about full model completion. No external numerical solver or fabricated citation was introduced.

## Integrated field and controller

The real idealized orbital field, normalized B-dot controller and team_adapter are implemented. Existing baseline step evidence is retained at data/processed/production_validation; the 1 s step applies only to the recorded baseline and regimes. Broader sweep verification remains pending. Both numerical APIs remain available. See docs/INTEGRATION.md for merged validation and evidence provenance.

## Regenerated Stage 3 gate

The historical status above is superseded for numerical pilot entry by
[STAGE3_VERIFICATION.md](STAGE3_VERIFICATION.md). Fresh canonical and high-spin
six-orbit refinements accept 0.25 s, with two successive passing halvings in
all three cases and a separate output-grid audit. The canonical 0.1 A m^2 bound
is inactive at all evaluated stages at that step; this is not generalized to
the ensemble. `configs/verification.json` contains measured evidence digests
and the exact tested source commit/tree. The real 108-case pilot and its
runtime/accuracy review remain required before production.
