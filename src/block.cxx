#include "block.h"

#include "math/nemlmath.h"

namespace neml {

int block_evaluate(
    std::shared_ptr<NEMLModel> model,
    size_t nblock,
    const double * const e_np1, const double * const e_n,
    const double * const T_np1, const double * const T_n,
    double t_np1, double t_n,
    double * const s_np1, const double * const s_n,
    double * const h_np1, const double * const h_n,
    double * const A_np1,
    double * const u_np1, const double * const u_n,
    double * const p_np1, const double *  p_n)
{
  // I am (apparently) willing to trade memory for time
  double * e_np1_local = new double [nblock * 6];
  double * e_n_local = new double [nblock *6];
  double * s_np1_local = new double [nblock * 6];
  double * s_n_local = new double [nblock * 6];
  double * A_np1_local = new double [nblock * 6 * 6];
  
  t2m(e_np1, e_np1_local, nblock);
  t2m(e_n, e_n_local, nblock);
  t2m(s_n, s_n_local, nblock);
  
  size_t nh = model->nstore();

  int * ier = new int[nblock];

#ifdef USE_OMP
#pragma omp parallel for
#endif
  for (size_t i = 0; i < nblock; i++) {
    ier[i] = model->update_sd(
        &e_np1_local[i*6], &e_n_local[i*6], T_np1[i], T_n[i], t_np1, t_n,
        &s_np1_local[i*6], &s_n_local[i*6], &h_np1[i*nh], &h_n[i*nh],
        &A_np1_local[i*36], u_np1[i], u_n[i], p_np1[i], p_n[i]);
  }

  for (size_t i = 0; i < nblock; i++) {
    if (ier[i] != 0) {
      int error = ier[i];
      delete [] ier;
      delete [] e_np1_local;
      delete [] e_n_local;
      delete [] s_np1_local;
      delete [] s_n_local;
      delete [] A_np1_local; 
      return error;
    }
  }
  
  delete [] ier;

  m2t(s_np1_local, s_np1, nblock);
  m42t4(A_np1_local, A_np1, nblock);

  // Free the temps
  delete [] e_np1_local;
  delete [] e_n_local;
  delete [] s_np1_local;
  delete [] s_n_local;
  delete [] A_np1_local;
  
  return 0;
}

void t2m(const double * const tensor, double * const mandel, size_t nblock)
{
  // Input: nx3x3 as a n x 9
  // Output: nx6 as a n x 6
  mat_mat(nblock, 6, 9, tensor, t2m_array, mandel);
}

void m2t(const double * const mandel, double * const tensor, size_t nblock)
{
  // Input: nx6 as a nx6
  // Output: nx3x3 as a nx9
  mat_mat(nblock, 9, 6, mandel, m2t_array, tensor);
}

void m42t4(const double * const mandel, double * const tensor, size_t nblock)
{
  // Input: nx6x6 as a nx36
  // Ouptut: nx3x3x3x3 as a nx81
  mat_mat(nblock, 81, 36, mandel, m42t4_array, tensor);
}

} // namespace neml
