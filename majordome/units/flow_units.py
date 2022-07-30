# -*- coding: utf-8 -*-
from typing import Optional
import cantera as ct


class FlowUnits:
    """ Management of gas flow rate units for different applications.

    Conversion is performed assuming ideal gas law. Concentration at normal
    condition is multiplied by gas molar weight and this value is used as
    base conversion factor.

    Attributes
    ----------
    T_NORMAL : float
        Reference temperature for normal conditions, default is 288.15 K.
    T_STANDARD: float = 273.15
        Reference temperature for standard conditions, default is 273.15 K.
    P_STANDARD: float = ct.one_atm
        Reference pressure for standard conditions, default is 101325 Pa.
    """
    T_NORMAL: float = 288.15
    T_STANDARD: float = 273.15
    P_STANDARD: float = ct.one_atm

    @property
    def normal_concentration(self) -> float:
        """ Ideal gas concentration at normal conditions [kmol/m³]. """
        den = ct.gas_constant * self.__class__.T_NORMAL
        return self.__class__.P_STANDARD / den

    def normal_flow_to_mass_flow(
            self,
            q: float,
            mw: float
        ) -> float:
        """ Convert flow given in Nm³/h to kg/s for a solution.
        
        Parameters
        ----------
        q: float
            Flow rate to be converted in Nm³/h.
        mw: float
            Solution mean molecular weight in kg/kmol.

        Returns
        -------
        float
            Flow rate converted to kg/s.
        """
        return self.normal_concentration * mw * q / 3600

    def standard_flow_to_gas_speed(
            self, 
            q: float,
            T_work: Optional[float] = 298.15,
            P_work: Optional[float] = ct.one_atm,
            A_cross: Optional[float] = 1.0
        ) -> float:
        """ Convert laboratory gas flow in Scm³/min to mean speed in m/s.

        Parameters
        ----------
        q: float
            Flow rate to be converted in Scm³/min (sccm).
        T_work: Optional[float] = 298.15
            Reactor working temperature in kelvin [K].
        P_work: Optional[float] = ct.one_atm
            Reactor working pressure in pascal [Pa]
        A_cross: Optional[float] = 1.0
            Reactor cross sectional area in squared meters [m²].

        Returns
        -------
        float
            Equivalent gas speed in meters per second [m/s].
        """
        P = self.__class__.P_STANDARD
        T = self.__class__.T_STANDARD

        min_per_sec = 1 / 60
        m3_per_cm3 = 1 / 10**6

        Q = q * min_per_sec * m3_per_cm3 * (T_work / P_work) * (P / T)
        U = Q / A_cross
        
        return U
