#!/usr/bin/env python3

import sys
sys.path.append('..')

import numpy as np
import scipy.integrate as quad

from neml import solvers, models, elasticity, drivers, surfaces, hardening, ri_flow, creep

import matplotlib.pyplot as plt

def example1():
  # T is in hours, strain in percent, stress in MPa
  A = 1.85e-9
  n = 2.5
  m = 0.3

  smodel = creep.NortonBaileyCreep(A, n, m)
  model = creep.J2CreepModel(smodel, verbose = False)

  stress = 150.0
  temp = 300.0
  times = np.linspace(0, 500, 100)

  # Function to integrate out the scalar model
  def scalar_rate(e, t):
    return smodel.g(stress, e[0], t, temp)
  
  estart = 0.01
  strains = quad.odeint(scalar_rate, estart, times)
  plt.plot(times, strains, 'k-')

  vstrains = []
  vstresses = []

  stress = np.array([stress, 0, 0, 0, 0, 0])
  vstresses.append(stress)
  vstrains.append(np.array([estart, -0.5*estart, -0.5*estart, 0, 0, 0]))
  for i in range(1, len(times)):
    strain_next, A_next = model.update(stress, vstrains[-1], temp, temp, 
        times[i], times[i-1])
    vstresses.append(vstresses[-1])
    vstrains.append(strain_next)

  vstresses = np.array(vstresses)
  vstrains = np.array(vstrains)
  plt.plot(times, vstrains[:,0], 'r-')

  plt.show()

def example2():
  # T is in hours, strain in percent, stress in MPa
  A = 1.85e-10
  n = 2.5

  smodel = creep.PowerLawCreep(A, n)
  cmodel = creep.J2CreepModel(smodel)

  E = 150000.0
  nu = 0.3
  sY = 200.0
  H = E / 50.0

  elastic = elasticity.IsotropicLinearElasticModel(E, "youngs", nu,
      "poissons")
  surface = surfaces.IsoJ2()
  iso = hardening.LinearIsotropicHardeningRule(sY, H)
  flow = ri_flow.RateIndependentAssociativeFlow(surface, iso)

  pmodel = models.SmallStrainRateIndependentPlasticity(elastic, flow)
  
  smax = 250.0
  R = -0.5
  srate = 1.0 * 3600.0
  ncycles = 25
  hold = 25

  res1 = drivers.stress_cyclic(pmodel, smax, R, srate, ncycles, 
      hold_time = [0,hold])

  model = models.SmallStrainCreepPlasticity(elastic, pmodel, cmodel, verbose = False)

  res2 = drivers.stress_cyclic(model, smax, R, srate, ncycles, 
      hold_time = [0,hold], verbose = False)

  plt.plot(res1['strain'], res1['stress'], 'k-')
  plt.plot(res2['strain'], res2['stress'], 'r-')
  plt.show()

def example3():
  # T is in hours, strain in percent, stress in MPa
  A = 1.85e-10
  n = 2.5

  smodel = creep.PowerLawCreep(A, n)
  cmodel = creep.J2CreepModel(smodel)

  E = 150000.0
  nu = 0.3
  sY = 200.0
  H = E / 50.0

  elastic = elasticity.IsotropicLinearElasticModel(E, "youngs", nu,
      "poissons")
  surface = surfaces.IsoJ2()
  iso = hardening.LinearIsotropicHardeningRule(sY, H)
  flow = ri_flow.RateIndependentAssociativeFlow(surface, iso)

  pmodel = models.SmallStrainRateIndependentPlasticity(elastic, flow)
  
  smax = 250.0
  R = -0.5
  srate = 1.0 * 3600.0
  ncycles = 25
  hold = 25

  res1 = drivers.stress_cyclic(pmodel, smax, R, srate, ncycles, 
      hold_time = [0,hold])

  model = models.SmallStrainCreepPlasticity(elastic, pmodel, cmodel, verbose = False)

  res2 = drivers.stress_cyclic(model, smax, R, srate, ncycles, 
      hold_time = [0,hold], verbose = False)

  plt.plot(res1['strain'], res1['stress'], 'k-')
  plt.plot(res2['strain'], res2['stress'], 'r-')
  plt.show()

def example4():
  # T is in hours, strain in percent, stress in MPa
  A = 1.85e-10
  n = 2.5
  m = 0.3

  smodel = creep.PowerLawCreep(A, n)
  cmodel = creep.J2CreepModel(smodel)

  E = 150000.0
  nu = 0.3
  sY = 200.0
  H = E / 25.0

  elastic = elasticity.IsotropicLinearElasticModel(E, "youngs", nu,
      "poissons")
  surface = surfaces.IsoJ2()
  iso = hardening.LinearIsotropicHardeningRule(sY, H)
  flow = ri_flow.RateIndependentAssociativeFlow(surface, iso)

  pmodel = models.SmallStrainRateIndependentPlasticity(elastic, flow)
  model = models.SmallStrainCreepPlasticity(elastic, pmodel, cmodel)

  res = drivers.creep(model, 205.0, 3600.0, 100.0, verbose = False, 
      nsteps_up = 500)
  plt.plot(res['strain'], res['stress'])
  plt.show()

if __name__ == "__main__":
  example1()
  example2()
  example3()
  example4()
