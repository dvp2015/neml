import sys
sys.path.append('..')

from common import *

from neml import interpolate
import unittest

import numpy as np
import numpy.random as ra
import scipy.interpolate as inter

class BaseInterpolate(object):
  def test_derivative(self):
    d = self.interpolate.derivative(self.x)
    nd = differentiate(lambda x: self.interpolate(x), self.x)
    self.assertTrue(np.isclose(d, nd, rtol = 1.0e-3))

class TestPolynomialInterpolate(unittest.TestCase, BaseInterpolate):
  def setUp(self):
    self.n = 5
    self.coefs = list((ra.random((self.n,)) * 0.5 - 1.0) * 2.0)
    self.x = ra.random((1,))[0]
    self.interpolate = interpolate.PolynomialInterpolate(self.coefs)

  def test_interpolate(self):
    self.assertTrue(np.isclose(np.polyval(self.coefs, self.x),
      self.interpolate(self.x)))

class TestPiecewiseLinearInterpolate(unittest.TestCase, BaseInterpolate):
  def setUp(self):
    self.validx = [-10.0, -2.0, 1.0, 2.0, 5.0, 15.0]
    self.invalidx_1 = [-2.0, -10.0, 1.0, 2.0, 5.0, 15.0]
    self.invalidx_2 = [-10.0, -2.0, 1.0, 2.0, 5.0]
    self.points = [50.0, -25.0, 1.0, 0.0, 0.0, 10.0]

    self.x = 17.0

    self.valid = interpolate.PiecewiseLinearInterpolate(self.validx,
        self.points)
    self.invalid1 = interpolate.PiecewiseLinearInterpolate(self.invalidx_1,
        self.points)
    self.invalid2 = interpolate.PiecewiseLinearInterpolate(self.invalidx_2,
        self.points)
    self.interpolate = self.valid

  def test_valid(self):
    self.assertTrue(self.valid.valid)
    self.assertFalse(self.invalid1.valid)
    self.assertFalse(self.invalid2.valid)

  def test_interpolate(self):
    testinter = inter.interp1d(self.validx, self.points,
        bounds_error = False)
    xs = np.linspace(-15.0,20.0)
    ys1 = [self.valid(x) for x in xs]
    ys2 = testinter(xs)
    ys2[xs < self.validx[0]] = self.points[0]
    ys2[xs > self.validx[-1]] = self.points[-1]
    self.assertTrue(np.allclose(ys1, ys2))

class TestGenericPiecewiseInterpolate(unittest.TestCase, BaseInterpolate):
  def setUp(self):
    self.xs = [1.0,5.0]
    self.cvs = [-1.0,5.0,-2.0]
    self.fns = [interpolate.ConstantInterpolate(cv) for cv in self.cvs]

    self.interpolate = interpolate.GenericPiecewiseInterpolate(self.xs,
        self.fns)

    self.x = 4.0

  def test_interpolate(self):
    self.assertTrue(np.isclose(self.interpolate.value(0.0), self.cvs[0]))
    self.assertTrue(np.isclose(self.interpolate.value(4.0), self.cvs[1]))
    self.assertTrue(np.isclose(self.interpolate.value(10.0), self.cvs[2]))

class TestPiecewiseLogLinearInterpolate(unittest.TestCase, BaseInterpolate):
  def setUp(self):
    self.validx = [-10.0, -2.0, 1.0, 2.0, 5.0, 15.0]
    self.invalidx_1 = [-2.0, -10.0, 1.0, 2.0, 5.0, 15.0]
    self.invalidx_2 = [-10.0, -2.0, 1.0, 2.0, 5.0]
    self.points = [1.0e5, 1.0e0, 1.0e-1, 1.0e-6, 1.0e0, 1.0e2]
    self.invalidpoints = [1.0e5, 1.0e0, -1.0e-1, 1.0e-6, 1.0e0, 1.0e2]

    self.x = 17.0

    self.valid = interpolate.PiecewiseLogLinearInterpolate(self.validx,
        self.points)
    self.invalid1 = interpolate.PiecewiseLogLinearInterpolate(self.invalidx_1,
        self.points)
    self.invalid2 = interpolate.PiecewiseLogLinearInterpolate(self.invalidx_2,
        self.points)
    self.invalid3 = interpolate.PiecewiseLogLinearInterpolate(self.validx,
        self.invalidpoints)
    self.interpolate = self.valid

  def test_valid(self):
    self.assertTrue(self.valid.valid)
    self.assertFalse(self.invalid1.valid)
    self.assertFalse(self.invalid2.valid)
    self.assertFalse(self.invalid3.valid)

  def test_interpolate(self):
    testinter = inter.interp1d(self.validx, np.log(self.points),
        bounds_error = False)
    xs = np.linspace(-15.0,20.0)
    ys1 = [self.valid(x) for x in xs]
    yp = testinter(xs)
    yp[xs < self.validx[0]] = np.log(self.points[0])
    yp[xs > self.validx[-1]] = np.log(self.points[-1])
    ys2 = np.exp(yp)
    print(ys1)
    print(ys2)
    self.assertTrue(np.allclose(ys1, ys2))

class TestConstantInterpolate(unittest.TestCase, BaseInterpolate):
  def setUp(self):
    self.v = ra.random((1,))[0]
    self.interpolate = interpolate.ConstantInterpolate(self.v)
    self.x = ra.random((1,))[0]

  def test_interpolate(self):
    self.assertTrue(np.isclose(self.v, self.interpolate(self.x)))

class TestExpInterpolate(unittest.TestCase, BaseInterpolate):
  def setUp(self):
    self.A = 1.2
    self.B = 5.1
    self.interpolate = interpolate.ExpInterpolate(self.A, self.B)
    self.x = 0.5

  def test_interpolate(self):
    self.assertTrue(np.isclose(self.A * np.exp(self.B/self.x),
      self.interpolate(self.x)))

class TestMTSInterpolate(unittest.TestCase, BaseInterpolate):
  def setUp(self):
    self.y0 = 100.0
    self.D = 50.0
    self.x0 = 200.0

    self.interpolate = interpolate.MTSShearInterpolate(self.y0, self.D, self.x0)

    self.x = 300.0

  def test_interpolate(self):
    should = self.y0 - self.D / (np.exp(self.x0 / self.x) - 1.0)
    act = self.interpolate(self.x)
    self.assertTrue(np.isclose(should, act))

class TestWorkRateFunc(unittest.TestCase, BaseInterpolate):
  def setUp(self):
    self.A = 1.0
    self.B = 5.0
    self.N = 2.0
    self.interpolate = interpolate.WorkRateFunc(self.A, self.B, self.N)
    self.x = 10.0

  def test_interpolate(self):
    self.assertTrue(np.isclose(np.power(self.A * self.x + self.B, self.N),
      self.interpolate(self.x)))
