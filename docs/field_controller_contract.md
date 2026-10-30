# Orbit field and controller connection

This document fixes the proposed technical contract for Person 3's modules. It records the baseline conventions and acceptance checks. No teammate has been messaged and no production field or controller acceptance has been claimed.

## Canonical values and runtime keys

Read configs/baseline.json through src.config.load_config. Angles and angular velocities are in radians and radians per second. Every input has a provenance note. The radius, gravity parameter, Earth rotation rate, ideal equatorial field scale, and dipole tilt are preliminary study inputs. They are not a dated geomagnetic model.

Use src.config.runtime_config to bind callbacks. Its keys are inertia, orbit, magnetic, controller_settings, field_model, and controller. The orbit and magnetic dictionaries retain their SI key names from the JSON. The controller_settings dictionary contains law, gain_kg_m2_s, max_dipole_a_m2, and saturation. Numerical settings remain separate.

## Geometry and epoch

The inertial orbit uses active right handed rotations R3(raan) R1(inclination). The argument of latitude is n t plus phase. The initial Earth rotation angle is earth_rotation_phase_rad. Simulation time zero is a chosen phase origin with no calendar epoch. The dipole axis rotates around inertial axis three.

The quaternion matrix is passive and maps inertial components into body components. A positive quarter turn about axis three maps inertial x into negative body y.

## Total field derivative

Let r be position, rhat its unit direction, d the unit dipole axis, b the equatorial strength at orbital radius, and g the inner product of d and rhat. For the circular orbit, b is constant. The following identities specify the analytic derivative.

1. Position velocity follows the derivative of the prescribed circular orbit.
2. The unit radial derivative is velocity divided by orbital radius.
3. The dipole axis derivative is Earth rotation rate times the cross product of inertial axis three with d.
4. The derivative of g is the sum of the inner products of dipole derivative with rhat and d with radial derivative.
5. The field derivative plus b times dipole derivative equals 3b times the sum of g derivative times rhat and g times radial derivative.

The field callback returns inertial field and this total derivative. Dynamics applies the body rotation correction once. The controller receives the corrected body derivative and must not apply it again.

## Controller convention

Use the normalized B dot law specified in the premise. Gain units are kilogram metres squared per second. The numeric value is not interchangeable with an unnormalized gain. Saturation limits total vector magnitude. Return raw_dipole, dipole, torque, and saturated using the callback signature in docs/dynamics_interface.md.

No gain tuning or guarantee of recovery is asserted by the baseline. A static inertial field provides a useful control power identity, but orbital field variation changes that identity.

## Acceptance before production runs

1. Verify orbit radius, period, unit dipole axis, and equatorial versus polar field strength.
2. Compare the analytic total field derivative against independent centered differences over a range of difference intervals.
3. Verify the known quaternion transformation and the body rotation correction.
4. Verify torque orthogonality, dipole bounds, zero command, clipping boundaries, and raw command units.
5. Run the static field energy identity test and explain why it does not establish monotonic energy for all orbital cases.
6. Supply the real callbacks to runtime_config and run the seven component rhs at multiple times and attitudes.
7. Combine with Person 2's integrator and complete convergence and production step selection before engineering sweeps.

The idealized production callbacks are now implemented in src/orbit_field.py and src/controller.py. Independent geometry, derivative, saturation and static field power tests exercise these implementations. Full model refinement evidence is recorded separately and final team review remains required. Earlier artificial callback tests retain their limited interface scope.
