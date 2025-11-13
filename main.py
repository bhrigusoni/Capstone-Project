"""
Main entry point for the ODE Solver project
Supports both Linear and Non-linear ODEs
"""
from ode_solver.solver import ODESolver
from ode_solver.visualization import plot_solution
from ode_solver.order_comparison import compare_orders


import sympy as sp
import numpy as np

def main():
    """
    Main entry point for the ODE solver program.
    - Prompts the user for one or more ODEs in terms of y(x) and x.
    - Parses each ODE string into a sympy expression.
    - Analyzes each ODE for order, linearity, and coefficient type.
    - For constant-coefficient linear ODEs, computes and displays the auxiliary equation and its roots.
    - Attempts to find an analytical solution using sympy's dsolve.
    - If analytical solution is not found, attempts a numerical solution.
    - Plots the solution(s) using matplotlib. If multiple ODEs are entered, compares them using compare_orders.
    """
    print("""
================================================================================
Welcome to the General ODE Solver!
================================================================================
Enter one or more ODEs in terms of y(x), supporting BOTH LINEAR and NON-LINEAR equations.

Examples:
  Linear (constant-coeff):  y'' - 3*y' + 2*y = 0
  Linear (variable-coeff):  x*y'' - 3*y' + 2*y = 0
  Non-linear ODE:   y' = y**2 (separable)
  Non-linear ODE:   y'' + y**3 = 0 (Duffing equation)
  Non-linear ODE:   y' - x*y**2 = 0 (Riccati-like)

Use y for the function and x for the variable.
Enter the equation as: LHS = RHS (or just LHS if RHS=0)
================================================================================
""")
    # Ask user if they want to compare multiple ODEs
    compare_mode = input("Do you want to compare solutions of multiple ODEs? (y/n): ").strip().lower()
    ode_strs = []
    if compare_mode == 'y':
        n = input("How many ODEs do you want to compare? (Enter a number >=2): ").strip()
        try:
            n = int(n)
            if n < 2:
                print("Need at least 2 ODEs to compare. Exiting.")
                return
        except Exception:
            print("Invalid number. Exiting.")
            return
        for i in range(n):
            ode_input = input(f"Enter ODE #{i+1}: ").strip()
            if not ode_input:
                print("No ODE provided. Exiting.")
                return
            ode_strs.append(ode_input)
    else:
        ode_str = input("Enter the ODE: ").strip()
        if not ode_str:
            print("No ODE provided. Exiting.")
            return
        ode_strs = [ode_str]

    # Parse and solve each ODE
    import re
    x = sp.symbols('x')
    y = sp.Function('y')
    solutions = []
    labels = []
    for idx, ode_str in enumerate(ode_strs):
        ode_str_orig = ode_str
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
            print(f"Error parsing ODE #{idx+1}: {e}")
            return
        solver = ODESolver(ode_expr, y, x)
        print(f"\n{'='*80}\nPARSED ODE #{idx+1} (LHS = 0):\n{'='*80}")
        sp.pprint(ode_expr)
        # Analyze the ODE
        analysis = solver.analyze()
        print(f"\n{'='*80}\nODE ANALYSIS (ODE #{idx+1}):\n{'='*80}")
        print(f"Order: {analysis['order']}")
        print(f"Is Linear: {analysis['is_linear']}")
        if analysis['is_linear']:
            print("Type: LINEAR ODE")
            is_const_coeff = solver.is_constant_coefficient()
            if is_const_coeff:
                print("Coefficient Type: CONSTANT")
            else:
                print("Coefficient Type: VARIABLE")
        else:
            print("Type: NON-LINEAR ODE")
        # For LINEAR ODEs: show auxiliary equation and classification (only if constant-coefficient)
        if analysis['is_linear']:
            print(f"\n{'-'*80}\nLINEAR ODE ANALYSIS (ODE #{idx+1}):\n{'-'*80}")
            is_const_coeff = solver.is_constant_coefficient()
            if is_const_coeff:
                print("[CONSTANT-COEFFICIENT ODE - Computing auxiliary equation]")
                try:
                    aux_eq, roots = solver.solve_auxiliary()
                    if aux_eq is not None and roots is not None:
                        print("\nAuxiliary equation:")
                        sp.pprint(aux_eq)
                        print("= 0")
                        print(f"Roots: {roots}")
                        try:
                            root_types = solver.classify_roots()
                            if root_types is not None:
                                print(f"\nRoot classification:")
                                print(f"  Real roots: {root_types['real']}")
                                print(f"  Complex roots: {root_types['complex']}")
                                print(f"  Repeated roots: {root_types['repeated']}")
                        except Exception as e:
                            print(f"[INFO] Could not classify roots: {str(e)[:80]}")
                    else:
                        print("[INFO] Could not compute auxiliary equation")
                except Exception as e:
                    print(f"[ERROR] Error computing auxiliary equation: {str(e)[:100]}")
            else:
                print("[VARIABLE-COEFFICIENT ODE]")
                print("Note: Auxiliary equation method NOT applicable to variable-coefficient ODEs.")
                print("Using direct symbolic/numerical methods instead.")
        # Try to find analytical solution
        print(f"\n{'-'*80}\nSOLVING ODE #{idx+1}...\n{'-'*80}")
        sol_analytical = solver.general_solution()
        if sol_analytical is not None:
            print("\n[OK] ANALYTICAL SOLUTION FOUND:")
            print("-"*80)
            sp.pprint(sol_analytical)
            solution_method = "Analytical"
            sol_to_plot = sol_analytical
        else:
            print("\n[INFO] No closed-form analytical solution found.")
            print("Attempting numerical solution...")
            print("\nAttempting numerical solution with initial conditions: y(0)=1, y'(0)=0, ...")
            x_vals, y_vals = solver.numerical_solution(
                x0=0,
                y0=None,  # Default initial conditions
                x_span=(-10, 10)
            )
            if x_vals is not None and y_vals is not None:
                print("[OK] NUMERICAL SOLUTION FOUND")
                solution_method = "Numerical"
                sol_to_plot = (x_vals, y_vals)
            else:
                print("[FAILED] Unable to solve ODE (both analytical and numerical methods failed)")
                print("\nSuggestions:")
                print("  - Check if the ODE is correctly formatted")
                print("  - For non-linear ODEs, try simpler forms")
                print("  - Verify initial conditions are appropriate")
                return
        # Prepare for plotting
        if solution_method == "Analytical":
            rhs = sol_analytical.rhs
            constants = [s for s in rhs.free_symbols if s.name.startswith('C')]
            subs = {c: 1 if i == 0 else 0 for i, c in enumerate(constants)}
            rhs_num = rhs.subs(subs)
            f_lambdified = sp.lambdify(x, rhs_num, modules=['numpy'])
            x_vals = np.linspace(-10, 10, 400)
            y_vals = f_lambdified(x_vals)
            solutions.append(y_vals)
            labels.append(f"ODE #{idx+1} ({analysis['order']} order)")
        else:
            # Numerical solution
            solutions.append(y_vals)
            labels.append(f"ODE #{idx+1} ({analysis['order']} order)")
    # Visualization
    print("\n" + "="*80)
    print("VISUALIZATION:")
    print("="*80)
    try:
        if len(solutions) == 1:
            # Single ODE: plot as before
            plot_solution(np.linspace(-10, 10, 400), solutions[0], title=labels[0])
            print("[OK] Plot displayed successfully")
        else:
            # Multiple ODEs: compare
            compare_orders(np.linspace(-10, 10, 400), solutions, labels=labels, title="Comparison of ODE Solutions")
            print("[OK] Comparison plot displayed successfully")
    except Exception as e:
        print(f"[ERROR] Visualization failed: {e}")
        print("  But the solution(s) were found - check the console output above")


# USAGE INSTRUCTIONS:
# 1. Run: python main.py
# 2. Enter your ODE using y, y', y'' (up to y''''), e.g. y'' - 3*y' + 2*y = 0
# 3. The program will:
#    - Analyze the ODE (linear vs non-linear, constant vs variable coefficients)
#    - Attempt analytical solution (for linear ODEs using characteristic equation if applicable)
#    - Fall back to numerical solution if analytical fails
#    - Plot the solution
#
# SUPPORTED ODE TYPES:
# - Linear constant-coefficient ODEs (all orders) - Uses auxiliary equation
# - Linear variable-coefficient ODEs (most common types) - Uses symbolic/numerical methods
# - Non-linear separable ODEs
# - Non-linear equations solvable by SymPy's dsolve
# - Other non-linear ODEs (numerical solution)

if __name__ == "__main__":
    main()
