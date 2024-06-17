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

"""This module contains a class for implementing fossen_thor_i_handbook_of_marine_craft_hydrodynamics_and_motion_control
"""
from casadi import SX, horzcat, inv, sin,cos, fabs, Function, diag, pinv,substitute
from platform import machine, system
from diffUV.utils import operators as ops
from diffUV.utils import euler_ops as T
from diffUV.utils.operators import cross_pO, coriolis_lag_param
from diffUV.utils.symbols import *


class Base(object):
    func_opts = {}
    jit_func_opts = {"jit": True, "jit_options": {"flags": "-Ofast"}}
    # OS/CPU dependent specification of compiler
    if system().lower() == "darwin" or machine().lower() == "aarch64":
        jit_func_opts["compiler"] = "shell"

    def __init__(self, func_opts=None, use_jit=True):
        if func_opts:
            self.func_opts = func_opts
        if use_jit:
            # NOTE: use_jit=True requires that CasADi is built with Clang
            for k, v in self.jit_func_opts.items():
                self.func_opts[k] = v
        self._initialize_inertia_matrix()
        self.body_state_vector = x_nb

    def __repr__(self) -> str:
        return "differentiable underwater dynamics"
    
    def _initialize_inertia_matrix(self):
        """Internal method to compute the UV inertia matrix based on vehicle parameters."""
        M_rb = SX(6,6)
        S = cross_pO(r_g)
        M_rb[:3,:3] = m*SX.eye(3)
        M_rb[:3,3:] = -m*S
        M_rb[3:,:3] = m*S
        M_rb[3:,3:] = Ib_b
        __M = (M_rb + MA) 
        # apply symmetry considerations
        self.M = __M* sb_fft_config
        # apply yg= 0 and Ixy=Iyz=0
        self.M = substitute(self.M, y_g, SX(0))
        self.M = substitute(self.M, I_xy, SX(0))
        self.M = substitute(self.M, I_yz, SX(0))


    def body_inertia_matrix(self):
        """Compute and return the UV inertia matrix with configuration adjustments."""
        # M = Function("M", syms , [M], self.func_opts)
        return self.M
    
    def body_coriolis_centripetal_matrix(self):
        """Compute and return the Coriolis and centripetal matrix based on current vehicle state in body"""
        M = self.body_inertia_matrix()
        # C_rb = coriolis_lag_param(M, x_nb)
        # CA = coriolis_lag_param(MA, x_nb)
        # C = C_rb+CA
        C = coriolis_lag_param(M, x_nb)
        return C

    def body_restoring_vector(self):
        """Compute and return the hydrostatic restoring forces."""
        g = SX(6, 1)
        g[0, 0] = (W - B)*sin(thet)
        g[1, 0] = -(W - B)*cos(thet)*sin(phi)
        g[2, 0] = -(W - B)*cos(thet)*cos(phi)
        g[3, 0] = -(y_g*W - y_b*B)*cos(thet)*cos(phi) + \
            (z_g*W - z_b*B)*cos(thet)*sin(phi)
        g[4, 0] = (z_g*W - z_b*B)*sin(thet) + \
            (x_g*W - x_b*B)*cos(thet)*cos(phi)
        g[5, 0] = -(x_g*W - x_b*B)*cos(thet) * \
            sin(phi) - (y_g*W - y_b*B)*sin(thet)
        # For neutrally buoyant vehicles W = B
        return g

    def body_damping_matrix(self):
        """Compute and return the total damping forces, including both linear and nonlinear components in body"""
        linear_damping = -diag(vertcat(X_u,Y_v,Z_w,K_p,M_q,N_r))
        nonlinear_damping = -diag(vertcat(X_uu,Y_vv,Z_ww,K_pp,M_qq,N_rr))@fabs(x_nb)
        D_v = linear_damping + nonlinear_damping
        return D_v

    def body_forward_dynamics(self):
        body_acc = inv(self.body_inertia_matrix())@(tau_b - self.body_coriolis_centripetal_matrix()@x_nb - self.body_restoring_vector() -self.body_damping_matrix()@x_nb)
        return body_acc

    def body_inverse_dynamics(self):
        resultant_torque = self.body_inertia_matrix()@dx_nb + self.body_coriolis_centripetal_matrix()@x_nb + self.body_restoring_vector() + self.body_damping_matrix()@x_nb
        return resultant_torque
    
    def control_Allocation(self):
        u = inv(K)@pinv(Tc)@tau_b
        return u
    
    def thruster_input2generalized_Forces(self):
        tau = K@Tc@u
        return tau
    
    