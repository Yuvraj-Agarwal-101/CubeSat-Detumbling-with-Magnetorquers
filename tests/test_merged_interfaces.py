"""Check the actual merged model boundary without running an engineering study."""
import json
from pathlib import Path
import numpy as np
from src.experiments import generate_cases
from src.integrators import rk4
from src.numerics.integrators import integrate
from src.dynamics import rhs
from team_adapter import build_cases, rhs_for_case, project


def test_both_numerical_apis_advance_the_same_real_model():
    case=build_cases()[0]
    f=lambda t,y:rhs(t,y,case['config'])
    a=rk4(f,case['y0'],(0,.25),.1,projection=project)
    t,y,meta=integrate(lambda y,t:f(t,y),case['y0'],.25,.1,project=project)
    np.testing.assert_array_equal(a.times,t)
    np.testing.assert_allclose(a.states,y,rtol=0,atol=0)
    assert a.function_evaluations==meta['rhs_evaluations']==12
    assert np.all(np.isfinite(y))


def test_person4_generated_document_connects_to_real_adapter():
    config=json.loads(Path('configs/study.json').read_text())
    case=next(generate_cases(config,'demo'))
    derivative=rhs_for_case(0,np.asarray(case['y0']),case)
    assert derivative.shape==(7,)
    assert np.all(np.isfinite(derivative))
