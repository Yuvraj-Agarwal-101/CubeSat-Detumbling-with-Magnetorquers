import unittest
import numpy as np
from src.integrators import rk4
from tests.exact_cases import (exact_rotation, multiply, spherical_rhs,
    project_quaternion, quaternion_norm, attitude_error, rotation_matrix)


class IntegratorTests(unittest.TestCase):
    def test_stage_times_states_and_count(self):
        calls = []
        def f(t, y):
            calls.append((t, y.copy()))
            return t*y
        r = rk4(f, [1.], (0, .2), .2)
        np.testing.assert_allclose([t for t,y in calls], [0,.1,.1,.2])
        np.testing.assert_allclose([y[0] for t,y in calls], [1,1,1.01,1.0202])
        self.assertEqual(r.function_evaluations, 4)
        self.assertAlmostEqual(r.states[-1,0], 1.0202013333333333)

    def test_short_final_step(self):
        r = rk4(lambda t,y: np.ones_like(y), [2.], (1,2), .3)
        np.testing.assert_allclose(r.times, [1,1.3,1.6,1.9,2])
        self.assertEqual(r.times[-1], 2)
        self.assertAlmostEqual(r.states[-1,0], 3)
        self.assertEqual(r.function_evaluations, 16)

    def test_no_spurious_final_step(self):
        r = rk4(lambda t,y: y, [1.], (0,1), .1)
        self.assertEqual(len(r.times), 11)

    def test_projection_only_completed_steps(self):
        seen, projected = [], []
        def f(t,y):
            seen.append(y[0]); return np.ones(1)
        def project(y):
            projected.append(y.copy()); return np.zeros(1)
        r = rk4(f,[0.],(0,2),1,projection=project,norm_diagnostic=lambda y: y[0])
        self.assertEqual(len(projected),2)
        np.testing.assert_allclose(seen,[0,.5,.5,1,0,.5,.5,1])
        np.testing.assert_allclose(r.preprojection_norm_error,[-1,0,0])
        np.testing.assert_allclose(r.states,0)

    def test_deterministic_and_input_preserved(self):
        y = np.array([1.])
        a = rk4(lambda t,y:y,y,(0,1),.1)
        b = rk4(lambda t,y:y,y,(0,1),.1)
        np.testing.assert_array_equal(a.states,b.states)
        np.testing.assert_array_equal(y,[1])

    def test_zero_interval(self):
        r = rk4(lambda t,y: self.fail('Unexpected call'), [1], (2,2), .1)
        self.assertEqual(r.function_evaluations,0)
        np.testing.assert_array_equal(r.states,[[1]])

    def test_invalid_inputs(self):
        for step in (0,-1,np.nan,np.inf):
            with self.assertRaises(ValueError): rk4(lambda t,y:y,[1],(0,1),step)
        for y in ([],[[1]],[np.nan]):
            with self.assertRaises(ValueError): rk4(lambda t,y:y,y,(0,1),.1)
        with self.assertRaises(ValueError): rk4(lambda t,y:y,[1],(1,0),.1)
        with self.assertRaises(ValueError): rk4(lambda t,y:y,[1],(1e16,1e16+4),.1)

    def test_invalid_callback_outputs(self):
        for f in (lambda t,y: np.array([np.inf]),lambda t,y: np.zeros(2)):
            with self.assertRaises(ValueError): rk4(f,[1],(0,1),.1)
        with self.assertRaises(ValueError):
            rk4(lambda t,y:y,[1],(0,1),.1,projection=lambda y:[np.nan])

    def test_scalar_fourth_order(self):
        errors = [abs(rk4(lambda t,y:t*y,[1],(0,2),h).states[-1,0]-np.exp(2))
                  for h in (.1,.05,.025)]
        self.assertTrue(np.all(np.log2(np.array(errors[:-1])/errors[1:]) > 3.8))

    def test_spherical_fourth_order_and_norm(self):
        y0=np.r_[[.8,.2,-.4,.4],[.3,-.4,.5]]
        errors=[]
        for h in (.5,.25,.125):
            r=rk4(spherical_rhs,y0,(0,20),h,projection=project_quaternion,norm_diagnostic=quaternion_norm)
            errors.append(attitude_error(r.states[-1,:4],exact_rotation(20,y0[:4],y0[4:])))
            np.testing.assert_allclose(np.linalg.norm(r.states[:,:4],axis=1),1,atol=3e-16)
            np.testing.assert_array_equal(r.states[:,4:],np.tile(y0[4:],(len(r.times),1)))
            self.assertGreater(np.max(np.abs(r.preprojection_norm_error)),0)
        np.testing.assert_allclose(np.log2(np.array(errors[:-1])/errors[1:]),4,atol=.03)

    def test_quarter_turn_convention(self):
        q=np.array([np.sqrt(.5),0,0,np.sqrt(.5)])
        np.testing.assert_allclose(rotation_matrix(q)@np.array([1,0,0]),[0,-1,0],atol=1e-15)
        np.testing.assert_allclose(rotation_matrix([1,0,0,0]),np.eye(3))

    def test_exact_reference_derivative(self):
        y0=np.r_[[.8,.2,-.4,.4],[.3,-.4,.5]]
        dt=1e-5
        derivative=(exact_rotation(dt,y0[:4],y0[4:])-exact_rotation(-dt,y0[:4],y0[4:]))/(2*dt)
        np.testing.assert_allclose(derivative,spherical_rhs(0,y0)[:4],rtol=1e-9,atol=1e-11)

    def test_zero_rate_and_quaternion_sign(self):
        q=np.array([.8,.2,-.4,.4])
        np.testing.assert_array_equal(exact_rotation(20,q,[0,0,0]),q)
        self.assertAlmostEqual(attitude_error(q,-q),0)
        np.testing.assert_allclose(multiply(q,[1,0,0,0]),q)
        with self.assertRaises(ValueError): project_quaternion(np.zeros(7))


if __name__=='__main__': unittest.main()
