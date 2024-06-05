from casadi import SX, horzcat, inv, sin,cos, fabs, Function
from diffUV.base import Base
from diffUV.utils.symbol import *
from diffUV.utils.operators import cross_product

class Dynamics(Base):
    def __init__(self):
        super().__init__()
        self._M = None

    def __repr__(self) -> str:
        """String representation of the Dynamics instance."""
        return f'{super().__repr__()} Dynamics'

    def _initialize_inertia_matrix(self):
        """Internal method to compute the UV inertia matrix based on vehicle parameters."""
        self._M = SX(6, 6)
        self._M[0, :] = horzcat(
            m - X_du, -X_dv, -X_dw, -X_dp, m*z_g - X_dq, -m*y_g - X_dr)
        self._M[1, :] = horzcat(-X_dv, m-Y_dv, -Y_dw, -
                                m*z_g-Y_dp, -Y_dq, m*x_g - Y_dr)
        self._M[2, :] = horzcat(-X_dw, -Y_dw, m - Z_dw,
                                m*y_g - Z_dp, -m*x_g - Z_dq, -Z_dr)
        self._M[3, :] = horzcat(-X_dp, -m*z_g-Y_dp, m*y_g -
                                Z_dp, I_x - K_dp, -I_yx - K_dq, -I_zx - K_dr)
        self._M[4, :] = horzcat(
            m*z_g - X_dq, -Y_dq, -m*x_g - Z_dq, -I_yx - K_dq, I_y - M_dq, -I_zy - M_dr)
        self._M[5, :] = horzcat(-m*y_g - X_dr, m*x_g -
                                Y_dr, -Z_dr, -I_zx - K_dr, -I_zy - M_dr, I_z - N_dr)

    def get_inertia_matrix(self):
        """Compute and return the UV inertia matrix with configuration adjustments."""
        self._initialize_inertia_matrix()
        # syms = [q] 
        M = self._M * star_board_config
        # M = Function("M", syms , [M], self.func_opts)
        return M


    def coriolis_centripetal_matrix(self):
        """Compute and return the Coriolis and centripetal matrix based on current vehicle state."""
        M = self.inertia_matrix()
        M11 = M[:3, :3]
        M12 = M[:3, 3:]
        M21 = M[3:, :3]
        M22 = M[3:, 3:]
        C = SX.zeros(6, 6)
        C[3:, :3] = -cross_product(M11@v_nb + M12@w_nb)
        C[:3, 3:] = -cross_product(M11@v_nb + M12@w_nb)
        C[3:, 3:] = -cross_product(M21@v_nb + M22@w_nb)
        return C
    
    def gvect(self):
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

    def damping(self):
        """Compute and return the total damping forces, including both linear and nonlinear components."""
        D = SX(6, 6)
        D[0, 0] = X_u
        D[1, 1] = Y_v
        D[2, 2] = Z_w
        D[3, 3] = K_p
        D[4, 4] = M_q
        D[5, 5] = N_r
        linear_damping = D@x_nb

        Dn_vars = [Dn1, Dn2, Dn3, Dn4, Dn5, Dn6]
        Dn_list = [(fabs(x_nb).T @ Dn @ x_nb) for Dn in Dn_vars]
        nonlinear_damping = vertcat(*Dn_list)

        damping = linear_damping + nonlinear_damping
        return damping
    
    def forward_dynamics(self):
        body_acc = inv(self.inertia_matrix())@(tau -self.coriolis_centripetal_matrix()@x_nb - self.gvect() -self.damping())
        return body_acc
    
    def inverse_dynamics(self):
        resultant_torque = self.inertia_matrix()@dx_nb + self.coriolis_centripetal_matrix()@x_nb + self.gvect() + self.damping()
        return resultant_torque