"""
ODE Parser and Preprocessor
Handles parsing and preprocessing of ODE strings for symbolic processing
"""
import re
import sympy as sp


def preprocess_ode_string(ode_str):
    """
    Preprocess ODE string to make it compatible with SymPy parsing.
    
    Args:
        ode_str (str): Raw ODE string from user input
        
    Returns:
        str: Preprocessed ODE string ready for sympify
        
    Handles:
    - Implicit multiplication (e.g., "2y" -> "2*y")
    - Derivative notation (y', y'', y''', y'''')
    - Equation balancing (moves RHS to LHS)
    """
    # Insert explicit multiplication where users omit it
    # (x**2)y'' -> (x**2)*y'' or xy' -> x*y'
    ode_str = re.sub(r'\)\s*(?=y)', ')*', ode_str)
    
    # Add '*' between an alphanumeric char and following 'y(' or 'y'
    ode_str = re.sub(r'(?<=[0-9A-Za-z_])\s*(?=y\s*\()', '*', ode_str)
    ode_str = re.sub(r'(?<=[0-9A-Za-z_])\s*(?=y(?!(\s*\()) )', '*', ode_str)
    
    # Conservative fallback: if pattern like 'x y' remains, replace space with '*'
    ode_str = re.sub(r'(?<=[0-9A-Za-z_])\s+(?=y)', '*', ode_str)
    
    # Remove explicit y(x) if user enters it, then replace with symbolic form
    ode_str = re.sub(r"y\s*\(\s*x\s*\)", "y", ode_str)
    
    # Replace derivative notation: y'''', y''', y'', y'
    ode_str = re.sub(r"y''''", "y(x).diff(x,4)", ode_str)
    ode_str = re.sub(r"y'''", "y(x).diff(x,3)", ode_str)
    ode_str = re.sub(r"y''", "y(x).diff(x,2)", ode_str)
    ode_str = re.sub(r"y'", "y(x).diff(x,1)", ode_str)
    
    # Only replace standalone y (not y(x))
    ode_str = re.sub(r"(?<![a-zA-Z0-9_])y(?![a-zA-Z0-9_\(])", "y(x)", ode_str)
    
    # If '=' is present, move all terms to LHS
    if '=' in ode_str:
        parts = ode_str.split('=')
        lhs = parts[0].strip()
        rhs = '='.join(parts[1:]).strip()  # In case '=' appears more than once
        ode_str = f"({lhs}) - ({rhs})"
    
    return ode_str


def parse_ode(ode_str):
    """
    Parse ODE string into SymPy expression.
    
    Args:
        ode_str (str): ODE string (raw or preprocessed)
        
    Returns:
        tuple: (ode_expression, x_symbol, y_function) or (None, None, None) on error
        
    Raises:
        Exception: If parsing fails
    """
    x = sp.symbols('x')
    y = sp.Function('y')
    
    # Preprocess the ODE string
    ode_str = preprocess_ode_string(ode_str)
    
    # Parse into SymPy expression
    try:
        ode_expr = sp.sympify(ode_str, locals={"x": x, "y": y})
        return ode_expr, x, y
    except Exception as e:
        raise Exception(f"Failed to parse ODE: {str(e)}")
