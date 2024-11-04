import numpy as np
import matplotlib.pyplot as plt
from transport_sn import solve
from sn_transport_functions import convergence_estimator
import tqdm
# This notebook will do standard convergence tests comparing cc and Gauss quadrature for a 1d steady problem

def RMSE(l1,l2):
    return np.sqrt(np.mean((l1-l2)**2))

def perform_convergence():
    N_ang_list = np.array([2,6,16,46])
    cc_err = np.zeros((3, N_ang_list.size))
    gauss_err = np.zeros((3, N_ang_list.size))
    N_cells = 100
    psib, phib, cell_centersb, musb, tableaub, Jb = solve(N_cells = N_cells, N_ang = 256, left_edge = 'source1', right_edge = 'source1', IC = 'cold', source = 'off',
            opacity_function = 'constant', wynn_epsilon = False, laststep = False,  L = 5.0, tol = 1e-13, source_strength = 1.0, sigma_a = 0.0, sigma_s = 1.0, sigma_t = 1.0,  strength = [1.0,0.0], maxits = 1e10, input_source = np.array([0.0]), quad_type='gauss')

    for iang, ang in tqdm.tqdm(enumerate(N_ang_list)):
        psicc, phicc, cell_centerscc, muscc, tableaucc, Jcc = solve(N_cells = N_cells, N_ang = ang, left_edge = 'source1', right_edge = 'source1', IC = 'cold', source = 'off',
            opacity_function = 'constant', wynn_epsilon = True, laststep = True,  L = 5.0, tol = 1e-13, source_strength = 1.0, sigma_a = 0.0, sigma_s = 1.0, sigma_t = 1.0,  strength = [1.0,0.0], maxits = 1e10, input_source = np.array([0.0]))
        
        psig, phig, cell_centersg, musg, tableaug, Jg = solve(N_cells = N_cells, N_ang = ang, left_edge = 'source1', right_edge = 'source1', IC = 'cold', source = 'off',
            opacity_function = 'constant', wynn_epsilon = False, laststep = False,  L = 5.0, tol = 1e-13, source_strength = 1.0, sigma_a = 0.0, sigma_s = 1.0, sigma_t = 1.0,  strength = [1.0,0.0], maxits = 1e10, input_source = np.array([0.0]), quad_type = 'gauss')
        
        gauss_err[0,iang] = RMSE(phig, phib)
        cc_err[0, iang] = RMSE(phicc, phib)
        gauss_err[1,iang] = RMSE(Jg[0], Jb[0])
        gauss_err[2,iang] = RMSE(Jg[1], Jb[1])
        cc_err[0, iang] = RMSE(phicc, phib)
        cc_err[1, iang] = RMSE(Jb[0], Jcc[0])
        cc_err[2, iang] = RMSE(Jb[1], Jcc[1])

    phi_err_estimate = np.zeros((N_ang_list.size, N_cells))
    err_estimate = np.zeros(N_ang_list.size)
    for ix in range(N_cells):
        phi_err_estimate[:, ix] = estimate_error(N_ang_list, tableaucc)
    for ang in range(N_ang_list.size):
        err_estimate[ang] = RMSE(phi_err_estimate[ang,:], phi_err_estimate[ang,:]*0)

    plt.figure('Scalar flux')
    plt.loglog(N_ang_list, cc_err[0], '-^', mfc = 'none')
    plt.loglog(N_ang_list, gauss_err[0], '-o', mfc = 'none')
    plt.loglog(N_ang_list, err_estimate, '-s', mfc = 'none')
    print(err_estimate)
    plt.savefig('flux_converge.pdf')
    plt.show()

    plt.figure('J')
    plt.loglog(N_ang_list, cc_err[1], 'r--^', mfc = 'none',  label = 'left')
    plt.loglog(N_ang_list, gauss_err[1], 'b--o', mfc = 'none',  label = 'left')
    plt.loglog(N_ang_list, cc_err[2], 'g-^', mfc = 'none',  label = 'right')
    plt.loglog(N_ang_list, gauss_err[2], 'y-o', mfc = 'none', label = 'right')
    # plt.legend()
    plt.savefig('J_converge.pdf')
    plt.show()


def estimate_error(ang_list, tableau):
    err_estimate = np.zeros(ang_list.size)
    for ia in range(2, ang_list.size):
        print(tableau[1:, 1][0:ia])
        err_estimate[ia] = convergence_estimator(ang_list[0:ia], tableau[1:, 1][0:ia])
    return err_estimate
