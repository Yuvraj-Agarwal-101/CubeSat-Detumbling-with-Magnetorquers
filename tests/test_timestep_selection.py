import unittest
import numpy as np
from studies.timestep_selection import sampled_metrics, compare, select_step


class MetricScreeningTests(unittest.TestCase):
    def metric(self,t,rates,hold=600):
        y=np.zeros((len(t),7)); y[:,0]=1; y[:,4]=rates
        return sampled_metrics(np.array(t),y,np.zeros((len(t),3)),np.zeros(len(t)),1,hold)

    def test_full_hold_required(self):
        self.assertFalse(self.metric([0,100,699],[2,.5,.5])['success'])
        self.assertEqual(self.metric([0,100,700],[2,.5,.5])['detumbling_time_s'],100)

    def test_excursion_resets_hold(self):
        self.assertEqual(self.metric([0,400,500,600,1200],[.5,.5,2,.5,.5])['detumbling_time_s'],600)

    def test_threshold_equality_satisfies_the_stated_criterion(self):
        self.assertTrue(self.metric([0,600],[1,1])['success'])

    def test_time_weighting(self):
        y=np.zeros((3,7))
        m=sampled_metrics(np.array([0,1,4]),y,np.zeros((3,3)),[0,1,1],1,600)
        self.assertAlmostEqual(m['saturation_fraction'],.875)

    def test_missing_time_and_classification(self):
        a={'success':False,'detumbling_time_s':None}
        b={'success':True,'detumbling_time_s':10}
        tolerances={'detumbling_time_s':{'absolute':1,'relative':.01}}
        self.assertFalse(compare(a,b,tolerances)['pass'])
        self.assertTrue(compare(a,a,tolerances)['pass'])

    def test_absolute_tolerance_at_zero(self):
        a={'success':True,'peak_torque_Nm':1e-11}
        b={'success':True,'peak_torque_Nm':0}
        self.assertTrue(compare(a,b,{'peak_torque_Nm':{'absolute':1e-10,'relative':.01}})['pass'])

    def test_two_refinements_and_success_required(self):
        record=dict(regime_check_pass=True,comparisons=[{'pass':True},{'pass':False},{'pass':True}],
                    runs=[{'metrics':{'success':True}}]*4)
        self.assertIsNone(select_step([record],[4,2,1,.5]))
        record['comparisons'][1]['pass']=True
        self.assertEqual(select_step([record],[4,2,1,.5]),4)
        record['runs']=[{'metrics':{'success':False}}]*4
        self.assertIsNone(select_step([record],[4,2,1,.5]))


if __name__=='__main__': unittest.main()
