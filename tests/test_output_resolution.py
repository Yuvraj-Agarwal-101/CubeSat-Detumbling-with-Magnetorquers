import numpy as np
import pytest
from studies.complete_verification import interpolated_hold, crossing_fraction
from studies.baseline_confirmation import compare_reference


def test_hold_starts_at_interior_crossing_and_must_finish():
    t=np.array([0.,2.,4.,6.]);rate=np.array([2.,0.,0.,0.])
    assert interpolated_hold(t,rate,1.,5.)==pytest.approx(1.)
    assert interpolated_hold(t,rate,1.,5.1) is None


def test_excursion_resets_interpolated_hold():
    t=np.array([0.,2.,4.,6.,8.]);rate=np.array([0.,0.,2.,0.,0.])
    assert interpolated_hold(t,rate,1.,3.)==pytest.approx(0.)
    assert interpolated_hold(t,rate,1.,3.01) is None


def test_equality_plateau_matches_person4_convention():
    assert interpolated_hold(np.array([0.,600.]),np.array([1.,1.]),1.,600.)==0.


def test_saturation_duration_uses_interpolated_crossing():
    assert crossing_fraction(np.array([0.,4.]),np.array([0.,4.]),1.)==pytest.approx(.75)
    assert crossing_fraction(np.array([0.,4.]),np.array([4.,0.]),1.)==pytest.approx(.75)


def test_nonuniform_output_intervals_are_time_weighted():
    assert crossing_fraction(np.array([0.,1.,5.]),np.array([0.,2.,2.]),1.)==pytest.approx(.9)


def test_reference_comparison_tolerates_roundoff_only():
    assert compare_reference({'success':True,'rate':.002+2e-17},{'success':True,'rate':.002})
    assert not compare_reference({'success':True,'rate':.0021},{'success':True,'rate':.002})


def test_reference_comparison_rejects_changed_classification():
    assert not compare_reference({'success':False},{'success':True})
