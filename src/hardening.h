#ifndef HARDENING_H
#define HARDENING_H

#include <cstddef>
#include <memory>
#include <vector>

namespace neml {

/// Interface for a generic hardening rule
//    1) Take alpha to q
//    2) Give the gradient of that function
class HardeningRule {
 public:
  virtual size_t nhist() const = 0;
  virtual int init_hist(double * const alpha) const = 0;
  virtual int q(const double * const alpha, double T, double * const qv) const = 0;
  virtual int dq_da(const double * const alpha, double T, double * const dqv) const = 0;
};

/// Isotropic hardening rules
class IsotropicHardeningRule: public HardeningRule {
 public:
  virtual size_t nhist() const;
  virtual int init_hist(double * const alpha) const;
  virtual int q(const double * const alpha, double T, double * const qv) const = 0;
  virtual int dq_da(const double * const alpha, double T, double * const dqv) const = 0;
};

/// Linear, isotropic hardening
class LinearIsotropicHardeningRule: public IsotropicHardeningRule {
 public:
  LinearIsotropicHardeningRule(double s0, double K);
  virtual int q(const double * const alpha, double T, double * const qv) const;
  virtual int dq_da(const double * const alpha, double T, double * const dqv) const;

  double s0() const;
  double K() const;
 private:
  const double s0_, K_;
};

/// Voce isotropic hardening
class VoceIsotropicHardeningRule: public IsotropicHardeningRule {
 public:
  VoceIsotropicHardeningRule(double s0, double R, double d);
  virtual int q(const double * const alpha, double T, double * const qv) const;
  virtual int dq_da(const double * const alpha, double T, double * const dqv) const;

  double s0() const;
  double R() const;
  double d() const;

 private:
  const double s0_, R_, d_;

};

class KinematicHardeningRule: public HardeningRule {
 public:
  virtual size_t nhist() const;
  virtual int init_hist(double * const alpha) const;
  virtual int q(const double * const alpha, double T, double * const qv) const = 0;
  virtual int dq_da(const double * const alpha, double T, double * const dqv) const = 0;
};

class LinearKinematicHardeningRule: public KinematicHardeningRule {
 public:
  LinearKinematicHardeningRule(double H);
  virtual int q(const double * const alpha, double T, double * const qv) const;
  virtual int dq_da(const double * const alpha, double T, double * const dqv) const;

  double H() const;

 private:
  const double H_;
};

class CombinedHardeningRule: public HardeningRule {
 public:
  CombinedHardeningRule(std::shared_ptr<IsotropicHardeningRule> iso,
                        std::shared_ptr<KinematicHardeningRule> kin);
  virtual size_t nhist() const;
  virtual int init_hist(double * const alpha) const;
  virtual int q(const double * const alpha, double T, double * const qv) const;
  virtual int dq_da(const double * const alpha, double T, double * const dqv) const;

 private:
  std::shared_ptr<IsotropicHardeningRule> iso_;
  std::shared_ptr<KinematicHardeningRule> kin_;
};

/// ABC of a non-associative hardening rule
class NonAssociativeHardening {
 public:
  virtual size_t ninter() const = 0; // How many "q" variables it spits out
  virtual size_t nhist() const = 0; // How many internal variables it stores

  virtual int init_hist(double * const alpha) const = 0;

  virtual int q(const double * const alpha, double T, double * const qv) const = 0;
  virtual int dq_da(const double * const alpha, double T, double * const qv) const = 0;

  virtual int h(const double * const s, const double * const alpha, double T,
                double * const hv) const = 0;
  virtual int dh_ds(const double * const s, const double * const alpha, double T,
                double * const dhv) const = 0;
  virtual int dh_da(const double * const s, const double * const alpha, double T,
                double * const dhv) const = 0;
};

/// Chaboche model: generalized Frederick-Armstrong
//    This model degenerates to Frederick-Armstrong for n = 1
class Chaboche {
 public:
  Chaboche(std::shared_ptr<IsotropicHardeningRule> iso,
                     int n, const double * const c, const double * const r);

  virtual size_t ninter() const; // How many "q" variables it spits out
  virtual size_t nhist() const; // How many internal variables it stores

  virtual int init_hist(double * const alpha) const;

  virtual int q(const double * const alpha, double T, double * const qv) const;
  virtual int dq_da(const double * const alpha, double T, double * const qv) const;

  virtual int h(const double * const s, const double * const alpha, double T,
                double * const hv) const;
  virtual int dh_ds(const double * const s, const double * const alpha, double T,
                double * const dhv) const;
  virtual int dh_da(const double * const s, const double * const alpha, double T,
                double * const dhv) const;

  // Getters
  int n() const;
  const std::vector<double> & c() const;
  const std::vector<double> & r() const;

 private:
  void backstress_(const double * const alpha, double * const X) const;

  std::shared_ptr<IsotropicHardeningRule> iso_;
  const int n_;
  const std::vector<double> c_, r_;
};


} // namespace neml

#endif // HARDENING_H