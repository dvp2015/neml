import sys
sys.path.append('..')

from neml import creep
import unittest

from common import *

import numpy as np
import numpy.linalg as la

class CommonScalarCreep(object):
  """
    Common tests to impose on scalar creep laws.
  """
  def test_dg_ds(self):
    dfn = lambda x: self.model.g(x, self.e, self.t, self.T)
    nderiv = differentiate(dfn, self.s)
    cderiv = self.model.dg_ds(self.s, self.e, self.t, self.T)
    self.assertTrue(np.isclose(nderiv, cderiv, rtol = 1.0e-4))

  def test_dg_de(self):
    dfn = lambda x: self.model.g(self.s, x, self.t, self.T)
    nderiv = differentiate(dfn, self.e)
    cderiv = self.model.dg_de(self.s, self.e, self.t, self.T)
    self.assertTrue(np.isclose(nderiv, cderiv, rtol = 1.0e-4))

  def test_dg_dt(self):
    dfn = lambda x: self.model.g(self.s, self.e, x, self.T)
    nderiv = differentiate(dfn, self.t)
    cderiv = self.model.dg_dt(self.s, self.e, self.t, self.T)
    self.assertTrue(np.isclose(nderiv, cderiv))

  def test_dg_dT(self):
    dfn = lambda x: self.model.g(self.s, self.e, self.t, x)
    nderiv = differentiate(dfn, self.T)
    cderiv = self.model.dg_dT(self.s, self.e, self.t, self.T)
    self.assertTrue(np.isclose(nderiv, cderiv))

class TestPowerLawCreep(unittest.TestCase, CommonScalarCreep):
  def setUp(self):
    self.A = 1.0e-6
    self.n = 5.0

    self.model = creep.PowerLawCreep(self.A, self.n) 

    self.T = 300.0
    self.e = 0.1
    self.s = 150.0
    self.t = 10.0

  def test_properties(self):
    self.assertTrue(np.isclose(self.A, self.model.A(self.T)))
    self.assertTrue(np.isclose(self.n, self.model.n(self.T)))

  def test_g(self):
    g_direct = self.model.g(self.s, self.e, self.t, self.T)
    g_calc = self.A * self.s ** (self.n)
    self.assertTrue(np.isclose(g_direct, g_calc))

class TestNortonBaileyCreep(unittest.TestCase, CommonScalarCreep):
  def setUp(self):
    self.A = 1.0e-6
    self.m = 0.25
    self.n = 5.0

    self.model = creep.NortonBaileyCreep(self.A, self.m, self.n) 

    self.T = 300.0
    self.e = 0.1
    self.s = 150.0
    self.t = 10.0

  def test_properties(self):
    self.assertTrue(np.isclose(self.A, self.model.A(self.T)))
    self.assertTrue(np.isclose(self.m, self.model.m(self.T)))
    self.assertTrue(np.isclose(self.n, self.model.n(self.T)))

  def test_g(self):
    g_direct = self.model.g(self.s, self.e, self.t, self.T)
    g_calc = self.m * self.A**(1.0/self.m) * self.s**(self.n/self.m) * self.e**((self.m-1.0)/self.m)
    self.assertTrue(np.isclose(g_direct, g_calc))

class CommonCreepModel(object):
  """
    Tests common to all creep models
  """
  def test_df_ds(self):
    dfn = lambda x: self.model.f(x, self.e, self.t, self.T)
    nderiv = differentiate(dfn, self.s)
    cderiv = self.model.df_ds(self.s, self.e, self.t, self.T)
    self.assertTrue(np.allclose(nderiv, cderiv, rtol = 1.0e-4))

  def test_df_de(self):
    dfn = lambda x: self.model.f(self.s, x, self.t, self.T)
    nderiv = differentiate(dfn, self.e)
    cderiv = self.model.df_de(self.s, self.e, self.t, self.T)
    self.assertTrue(np.allclose(nderiv, cderiv, rtol = 1.0e-4))

  def test_df_dt(self):
    dfn = lambda x: self.model.f(self.s, self.e, x, self.T)
    nderiv = differentiate(dfn, self.t)
    cderiv = self.model.df_dt(self.s, self.e, self.t, self.T)
    self.assertTrue(np.allclose(nderiv, cderiv))

  def test_df_dT(self):
    dfn = lambda x: self.model.f(self.s, self.e, self.t, x)
    nderiv = differentiate(dfn, self.T)
    cderiv = self.model.df_dT(self.s, self.e, self.t, self.T)
    self.assertTrue(np.allclose(nderiv, cderiv))

class TestJ2Creep(unittest.TestCase, CommonCreepModel):
  def setUp(self):
    self.A = 1.0e-10
    self.m = 0.25
    self.n = 5.0

    self.smodel = creep.NortonBaileyCreep(self.A, self.m, self.n)

    self.model = creep.J2CreepModel(self.smodel)

    self.s = np.array([100.0,-25.0,-5.0, 20.0,15.0,3.0])
    self.e = np.array([0.05, -0.01, -0.01, 0.025, 0.03, -0.01])
    self.T = 300.0
    self.t = 10.0

    tr = np.sum(self.s[:3])
    self.sdev = self.s - np.array([1,1,1,0,0,0]) * tr / 3.0
    self.se = np.sqrt(3.0/2.0) * la.norm(self.sdev)
    self.ee = np.sqrt(2.0/3.0) * la.norm(self.e)

  def test_f(self):
    f_direct = self.model.f(self.s, self.e, self.t, self.T)
    g_direct = self.smodel.g(self.se, self.ee, self.t, self.T)
    f_calc = g_direct * 3.0 / 2.0 * self.sdev / self.se

    self.assertTrue(np.allclose(f_direct, f_calc))

  def test_f_uni(self):
    """
      Make sure all our "effectives" work out correctly
    """
    s = np.array([100.0, 0, 0, 0, 0, 0])
    e = np.array([0.1, -0.05, -0.05, 0, 0, 0])
    f_direct = self.model.f(s, e, self.t, self.T)
    
    sdev = s - np.array([1,1,1,0,0,0]) * np.sum(s[:3]) / 3.0
    se = np.sqrt(3.0/2.0) * la.norm(sdev)
    ee = np.sqrt(2.0/3.0) * la.norm(e)

    g_direct = self.smodel.g(se, ee, self.t, self.T)
    
    self.assertTrue(np.isclose(g_direct, f_direct[0]))

    self.assertTrue(np.isclose(-g_direct/2.0, f_direct[1]))
    self.assertTrue(np.isclose(-g_direct/2.0, f_direct[2]))

    self.assertTrue(np.allclose([0,0,0], f_direct[3:]))

