# Copyright 2024, Edward Morgan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import numpy as np

class Params:
    thrust_config = np.array([[-0.707, -0.707, 0.707, 0.707, 0.0, 0.0, 0.0, 0.0],
        [0.707, -0.707, 0.707, -0.707, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 1.0, -1.0, -1.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, -0.218, -0.218, 0.218, 0.218],
        [0.0, 0.0, 0.0, 0.0, -0.12, 0.12, -0.12, 0.12],
        [0.1888, -0.1888, -0.1888, 0.1888, 0.0, 0.0, 0.0, 0.0]])
    
    # thrust_config = np.array([[0.707, 0.707, -0.707, -0.707, 0.0, 0.0, 0.0, 0.0],
    #                     [-0.707, 0.707, -0.707, 0.707, 0.0, 0.0, 0.0, 0.0],
    #                     [0.0, 0.0, 0.0, 0.0, -1.0, 1.0, 1.0,-1.0],
    #                     [0.06, -0.06, 0.06, -0.06, -0.218, -0.218, 0.218, 0.218],
    #                     [0.06, 0.06, -0.06, -0.06, 0.12, -0.12, 0.12, -0.12],
    #                     [-0.1888, 0.1888, 0.1888, -0.1888, 0.0, 0.0, 0.0, 0.0]])
    
    #thrust coefficient matrix
    K = np.diag([40, 40, 40, 40, 40, 40, 40, 40])

    # parameters in rigid body dynamics and restoring forces
    m = 11.5 #(kg)
    W = m*9.81 #(N)
    B = 114.8 #(N)
    rb  = np.array([0, 0, 0]) #(m)
    rg = np.array([0, 0, 0.02]) #(m)
    h = 0.254

    I_x = 0.16 #(kg m2)
    I_y = 0.16 #(kg m2)
    I_z = 0.16 #(kg m2)
    I_xz = 0

    Io = np.array([I_x, I_y, I_z, I_xz])

    # added mass parameters
    X_du = -5.5 #(kg)
    Y_dv = -12.7 #(kg)
    Z_dw = -14.57 #(kg)
    K_dp = -0.12 #(kg m2/rad)
    M_dq = -0.12 #(kg m2/rad)
    N_dr = -0.12 #(kg m2/rad)

    added_m = np.array([X_du, Y_dv, Z_dw, K_dp, M_dq, N_dr])
    coupl_added_m = np.array([0, 0, 0, 0, 0]) # assuming decoupling motion

    Xu = -4.03 #(Ns/m) 
    Yv = -6.22 #(Ns/m) 
    Zw = -5.18 #(Ns/m) 
    Kp = -0.07 #(Ns/rad) 
    Mq = -0.07 #(Ns/rad)
    Nr = -0.07 #(Ns/rad) 

    linear_dc = np.array([Xu, Yv, Zw, Kp,  Mq, Nr])

    Xuu = -18.18 #(Ns2/m2)
    Yvv = -21.66 #(Ns2/m2)
    Zww = -36.99 #(Ns2/m2)
    Kpp = -1.55 #(Ns2/rad2)
    Mqq = -1.55 #(Ns2/rad2)
    Nrr = -1.55 #(Ns2/rad2)

    quadratic_dc = np.array([Xuu, Yvv, Zww, Kpp, Mqq, Nrr])