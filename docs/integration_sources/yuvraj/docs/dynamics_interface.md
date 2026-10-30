# Dynamics integration contract

The reusable functions are `angular_acceleration(omega, torque, inertia)` and `rhs(t, y, config)` in `src/physics/dynamics.py`. Public imports through `src.dynamics` remain available. The physics module has no time integrator and no production field or controller implementation. Generic time methods are in src/numerics/integrators.py. The callback signatures below define the connection points for future production modules. They have not yet been verified against Person 3's code.

## State and units

The state is a real NumPy compatible array of shape `(7,)` containing scalar first quaternion components followed by body angular velocity. Quaternion order is `[s, vx, vy, vz]`. Angular velocity is in radians per second. The return value has shape `(7,)` containing quaternion derivatives followed by angular acceleration in radians per second squared.

The passive matrix `C_BI` maps inertial components into body components. Quaternion derivatives retain the supplied stage magnitude. Orientation evaluation normalizes a local copy without changing the state. The time integrator must handle any projection after its completed step.

## Required configuration entries

1. `inertia` is a real symmetric positive definite array of shape `(3, 3)` in kilogram metres squared. Full tensors are supported. Symmetry is checked with relative tolerance `1e-12` and zero absolute tolerance. The symmetric part must have strictly positive eigenvalues.
2. `field_model` is a pure callable with signature `field_model(t, config)`.
3. `controller` is a pure callable with signature `controller(t, q, omega, B_B, dB_B_dt, config)`.

Additional configuration entries pass through unchanged to both callbacks. The canonical case is now in configs/baseline.json. src.config.runtime_config binds callbacks and exports inertia, orbit, magnetic, and controller_settings. The numerical method, step size, and study success criteria remain separate from the physics dictionary.

## Field callback

Return a tuple or list containing `B_I` and `dB_I_dt`. Each vector has shape `(3,)`. Their units are tesla and tesla per second. The derivative is the total derivative along the prescribed orbit, including Earth rotation. It must not be just a derivative at fixed position.

Dynamics computes the body field as `C_BI @ B_I` and its derivative as `C_BI @ dB_I_dt - cross(omega, B_B)`. Do not apply the body rotation correction again in the controller.

## Controller callback

Receive the current time in seconds, the quaternion of shape `(4,)`, body rate of shape `(3,)`, body field of shape `(3,)`, body field derivative of shape `(3,)`, and the shared configuration. Array arguments are copies. The callback must return a mapping containing the following values.

1. `raw_dipole` is a finite body vector of shape `(3,)` in ampere metres squared.
2. `dipole` is the finite commanded body vector of shape `(3,)` in ampere metres squared.
3. `torque` is a finite body vector of shape `(3,)` in newton metres and must equal `cross(dipole, B_B)`.
4. `saturated` is a Python or NumPy boolean.

The controller owns the normalized B dot gain, saturation law, and their validation. Dynamics independently forms the physical cross product and checks reported torque using relative tolerance `1e-12` and absolute tolerance `1e-18` newton metres. Acceleration uses the independently formed torque.

## Evaluation and purity

Each call evaluates field and controller at exactly its supplied time and state. Both callbacks must be deterministic and must not mutate the shared configuration, retain evaluation history, or advance time. Numerical integrators must call `rhs` separately at every stage. A suitable derivative closure is shown below.

```python
from src.dynamics import rhs

def derivative(t, y):
    return rhs(t, y, config)
```

Missing callbacks and malformed callback outputs raise `ValueError`. No fallback field, fallback controller, or fixed torque is silently inserted. Test fixtures live only in `tests/test_dynamics.py` and do not constitute production control or field models.

## Reproduction

Run `.venv/bin/python -m pytest -q tests/test_dynamics.py` for the 62 instantaneous dynamics cases. Run `.venv/bin/python -m tools.check_project` for all 222 current cases and generated revision evidence. Run `.venv/bin/python run_all.py` for both numerical contributions and the pending production refinement connection point. Production magnetic trajectory checks and step selection remain pending.

The numerical integrator uses state first callbacks. Connect the public physical RHS with a function f(u, t) returning rhs(t, u, runtime). The projection callback is applied after completed steps only. Solver settings and runtime physics remain separate.
