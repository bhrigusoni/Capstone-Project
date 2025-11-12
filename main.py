"""
Main entry point for the ODE Solver project
"""
from ode_solver.solver import ODESolver
from ode_solver.visualization import plot_solution
from ode_solver.order_comparison import compare_orders


import sympy as sp

def main():
    print("""
Welcome to the General ODE Solver!
Enter an ODE in terms of y(x), e.g. y'' - 3*y' + 2*y = 0
Use y for the function and x for the variable.
Example: y'' - 3*y' + 2*y
""")
    # Get user input
    ode_str = input("Enter the ODE (LHS = 0): ")
    # Parse the ODE robustly using regex
    import re
    x = sp.symbols('x')
    y = sp.Function('y')
    # If '=' is present, move all terms to LHS
    if '=' in ode_str:
        parts = ode_str.split('=')
        lhs = parts[0].strip()
        rhs = '='.join(parts[1:]).strip()  # In case '=' appears more than once
        ode_str = f"({lhs}) - ({rhs})"
    # Replace y'''' (4th), y''' (3rd), y'' (2nd), y' (1st), y (0th)
    ode_str = re.sub(r"y\s*\(\s*x\s*\)", "y", ode_str)  # Remove explicit y(x) if user enters it
    ode_str = re.sub(r"y''''", "y(x).diff(x,4)", ode_str)
    ode_str = re.sub(r"y'''", "y(x).diff(x,3)", ode_str)
    ode_str = re.sub(r"y''", "y(x).diff(x,2)", ode_str)
    ode_str = re.sub(r"y'", "y(x).diff(x,1)", ode_str)
    # Only replace standalone y (not y(x))
    ode_str = re.sub(r"(?<![a-zA-Z0-9_])y(?![a-zA-Z0-9_\(])", "y(x)", ode_str)
    try:
        ode_expr = sp.sympify(ode_str, locals={"x": x, "y": y})
    except Exception as e:
        print(f"Error parsing ODE: {e}")
        return
    solver = ODESolver(ode_expr, y, x)
    print("\nParsed ODE (LHS = 0):")
    sp.pprint(ode_expr)

    # Extract homogeneous part: sum of all terms involving y or its derivatives
    y_terms = []
    for term in ode_expr.expand().as_ordered_terms():
        if term.has(y(x)):
            y_terms.append(term)
    if y_terms:
        homogeneous_expr = sum(y_terms)
    else:
        homogeneous_expr = ode_expr
    print("\nHomogeneous part used for analysis:")
    sp.pprint(homogeneous_expr)

    # Use homogeneous part for analysis and auxiliary equation
    solver_hom = ODESolver(homogeneous_expr, y, x)
    analysis = solver_hom.analyze()
    print(f"ODE Order: {analysis['order']}")
    print(f"Is Linear: {analysis['is_linear']}")
    print(f"Coefficients: {analysis['coefficients']}")
    aux_eq, roots = solver_hom.solve_auxiliary()
    print("Auxiliary equation:")
    sp.pprint(aux_eq)
    print("= 0")
    print(f"Roots: {roots}")
    root_types = solver_hom.classify_roots()
    print(f"Root classification: {root_types}")

    # Use full ODE for solution
    sol = solver.general_solution()
    print("General solution:")
    sp.pprint(sol)
    # Visualization (homogeneous solution only)
    try:
        # Substitute arbitrary constants with default values for plotting
        rhs = sol.rhs
        constants = [s for s in rhs.free_symbols if s.name.startswith('C')]
        subs = {c: 1 if i == 0 else 0 for i, c in enumerate(constants)}
        rhs_num = rhs.subs(subs)
        f_lambdified = sp.lambdify(x, rhs_num, modules=['numpy'])
        import numpy as np
        x_vals = np.linspace(-10, 10, 400)
        y_vals = f_lambdified(x_vals)
        plot_solution(x_vals, y_vals, title="ODE Solution (C1=1, others=0)")
    except Exception as e:
        print(f"Visualization failed: {e}")


# USAGE INSTRUCTIONS:
# 1. Run: python main.py
# 2. Enter your ODE using y, y', y'' (up to y'''', e.g. y'''' - y'' + y = 0)
# 3. The program will analyze, solve, and plot the solution.

if __name__ == "__main__":
    main()
