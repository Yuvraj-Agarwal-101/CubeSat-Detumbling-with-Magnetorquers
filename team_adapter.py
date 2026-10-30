"""Real idealized field/control integration for Person 2 and Person 4 studies."""
from copy import deepcopy
import numpy as np
from src.config import load_config, validate_config, initial_state, case_summary, runtime_config
from src.quaternion import rotation_matrix, normalize
from src.dynamics import rhs
from src.controller import controller
from src.orbit_field import field_model, frozen_inertial_field
from src.integrators import rk4


def diagnostics(t, y, config):
    b, db = config['field_model'](t, config)
    matrix = rotation_matrix(y[:4])
    body = matrix@b
    return controller(t, y[:4], y[4:], body, matrix@db-np.cross(y[4:],body), config)


def project(y):
    y = y.copy()
    y[:4] = normalize(y[:4])
    return y


def build_cases():
    cases = []
    for name, limit in [('unsaturated',1.), ('saturated',.01)]:
        document = deepcopy(load_config())
        document['physical']['controller']['max_dipole_a_m2'] = limit
        document['provenance']['physical.controller.max_dipole_a_m2'] = dict(
            classification='project_choice',note='Deterministic refinement case with '+name+' control')
        document = validate_config(document)
        summary = case_summary(document)
        cases.append(dict(name=name,regime=name,is_fixture=False,rhs=rhs,diagnostics=diagnostics,
                          config=runtime_config(document,field_model=field_model,controller=controller),
                          config_record=document,y0=initial_state(document),
                          t_span=[0.,summary['deadline_s']],orbital_period_s=summary['orbital_period_s'],
                          seed=None,callback_identifiers=dict(field_model='src.orbit_field:field_model',controller='src.controller:controller'),
                          intermediate_quaternion_policy='Normalize local matrix copy only; project state after completed steps'))
    return cases


def simulate(case, dt_s):
    """Person 4 contract. No trajectory stops early after detumbling."""
    document = validate_config(case['document'])
    mode = case.get('field_mode','orbital')
    if mode not in ('orbital','frozen_inertial'):
        raise ValueError('Unsupported field mode')
    field = field_model if mode == 'orbital' else frozen_inertial_field
    config = runtime_config(document,field_model=field,controller=controller)
    y0 = initial_state(document)
    if 'y0' in case and not np.allclose(case['y0'],y0,rtol=0,atol=1e-12):
        raise ValueError('Case initial state differs from recorded document')
    sol = rk4(lambda t,y:rhs(t,y,config),y0,(0,case_summary(document)['deadline_s']),dt_s,
               projection=project,norm_diagnostic=lambda y:np.linalg.norm(y[:4]))
    samples = [diagnostics(t,y,config) for t,y in zip(sol.times,sol.states)]
    return dict(t=sol.times,states=sol.states,raw_dipole=np.array([d['raw_dipole'] for d in samples]),
                dipole=np.array([d['dipole'] for d in samples]),torque=np.array([d['torque'] for d in samples]),
                preprojection_norm_error=sol.preprojection_norm_error)


def rhs_for_case(t, y, case):
    """Person 4's optional instantaneous callback for frozen Jacobian audits."""
    document = validate_config(case['document'])
    mode = case.get('field_mode','orbital')
    if mode not in ('orbital','frozen_inertial'):
        raise ValueError('Unsupported field mode')
    field = field_model if mode == 'orbital' else frozen_inertial_field
    return rhs(t,y,runtime_config(document,field_model=field,controller=controller))
