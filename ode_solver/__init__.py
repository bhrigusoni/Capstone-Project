"""
ODE Solver Package
------------------
This package provides tools for analyzing and solving ordinary differential equations (ODEs),
including support for both linear and non-linear ODEs, auxiliary equation construction, root classification,
analytical and numerical solution methods.
"""

from .solver import ODESolver
from .parser import parse_ode, preprocess_ode_string

__all__ = ['ODESolver', 'parse_ode', 'preprocess_ode_string']
