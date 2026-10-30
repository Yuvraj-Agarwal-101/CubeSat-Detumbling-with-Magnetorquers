"""Connection contract for Person 1, Person 3, and Person 4.

Copy this file to team_adapter.py at repository root. Implement build_cases()
using the team's actual modules. Do not set is_fixture=False for a fixture.

Each dictionary must have the following fields.
name                       Unique case name
regime                     'unsaturated' or 'saturated'
is_fixture                 False only for the independently verified full model
rhs                        Callable rhs(t, y, config), seven finite derivatives
diagnostics                Callable diagnostics(t, y, config), dictionary with
                           torque, raw_dipole, dipole, each shape (3,)
config                     Runtime config with inertia, field_model and
                           controller callbacks for src.dynamics.rhs.
config_record              JSON serializable complete physical configuration,
                           including mmax in A m^2, gain, inertia, orbit, field
                           constants and orientation, units and assumptions,
                           plus import paths identifying the callbacks.
y0                         Seven components, unit scalar first quaternion and
                           body angular velocity in rad/s
t_span                     [0.0, 6*orbital_period_s]
orbital_period_s           Physical orbital period used by the model
seed                       Explicit integer if random, otherwise None
intermediate_quaternion_policy
                           Description of matrix evaluation at stage states

The factory must return at least one full model case for each regime. Include
successful detumbling cases so timing convergence is actually measurable.
Case configurations must be final before production sweeps. The chosen gain
and dipole limit must actually yield the declared saturation regime.
The driver checks sampled saturation status, not all continuous crossings.

rhs must evaluate forcing and control at every call, without call history.
The integrator calls rhs at all four stages. diagnostics must be deterministic
and use the same control law as rhs. No routine may advance time through an
external numerical integrator. This template intentionally supplies no model.
"""


def build_cases():
    raise NotImplementedError('Connect actual teammate modules using the documented contract')
