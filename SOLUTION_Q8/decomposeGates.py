# import numpy as np
# from scipy.linalg import expm, norm
# from scipy.optimize import minimize


# def nadomestnaVrata(Rs):
#     # Pauli matrices
#     X = np.array([[0, 1], [1, 0]], dtype=complex)
#     Y = np.array([[0, -1j], [1j, 0]], dtype=complex)

#     def RX(theta):
#         return expm(-1j * theta/2 * X)

#     def RY(theta):
#         return expm(-1j * theta/2 * Y)

#     # Compute total unitary
#     U = np.eye(2, dtype=complex)
#     for axis, angle, _ in reversed(Rs):
#         if axis == 'RX':
#             U = RX(angle) @ U
#         elif axis == 'RY':
#             U = RY(angle) @ U

#     # Define the objective for 3-gate decomposition: RY(theta1) RX(phi) RY(theta2)

#     def objective(params):
#         theta1, phi, theta2 = params
#         U_approx = RY(theta1) @ RX(phi) @ RY(theta2)
#         return norm(U - U_approx)

#     # Initial guess
#     res = minimize(objective, x0=[0, 0, 0], method='BFGS')
#     theta1_opt, phi_opt, theta2_opt = res.x

#     # Compute final approximation and error
#     U_approx = RY(theta1_opt) @ RX(phi_opt) @ RY(theta2_opt)
#     error = norm(U - U_approx)
#     error_op = norm(U - U_approx, 2)

#     return U_approx

# # print("Optimal decomposition:")
# # print(f"('RY', {theta1_opt}, 0)")
# # print(f"('RX', {phi_opt}, 0)")
# # print(f"('RY', {theta2_opt}, 0)")
# # print(f"\nFrobenius error: {error:.2e}")
# # print(f"Operator error:  {error_op:.2e}")

import numpy as np
from scipy.linalg import expm, norm
from scipy.optimize import minimize


def nadomestnaVrata(Rs, error_threshold=1e-10):
    # Pauli matrices
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)

    def RX(theta):
        return expm(-1j * theta/2 * X)

    def RY(theta):
        return expm(-1j * theta/2 * Y)

    # Compute total unitary
    U = np.eye(2, dtype=complex)
    # print(len(Rs[0]))
    for tuple in Rs:  # right to left
        axis = tuple[0]
        angle = tuple[1]
        if axis == 'RX':
            U = U @ RX(angle)
        elif axis == 'RY':
            U = U @ RY(angle)

    # ---- Try 2-gate decomposition: RY(theta) RX(phi)
    def obj2(params):
        phi, theta = params
        U_approx = RY(theta) @ RX(phi)
        return norm(U - U_approx)

    res2 = minimize(obj2, x0=[0, 0], method='BFGS')
    phi2, theta2 = res2.x
    U2 = RY(theta2) @ RX(phi2)
    err2 = norm(U - U2)

    if err2 < error_threshold:
        return {
            'gates': [('RX', phi2, 0), ('RY', theta2, 0)],
            'unitary': U2,
            'error': err2,
            'num_gates': 2
        }

    # ---- Try 3-gate decomposition: RY(theta1) RX(phi) RY(theta2)
    def obj3(params):
        theta1, phi, theta2 = params
        U_approx = RY(theta1) @ RX(phi) @ RY(theta2)
        return norm(U - U_approx)

    res3 = minimize(obj3, x0=[0, 0, 0], method='BFGS')
    theta1, phi3, theta2 = res3.x
    U3 = RY(theta1) @ RX(phi3) @ RY(theta2)
    err3 = norm(U - U3)

    return {
        'gates': [('RY', theta1, 0), ('RX', phi3, 0), ('RY', theta2, 0)],
        'unitary': U3,
        'error': err3,
        'num_gates': 3
    }
