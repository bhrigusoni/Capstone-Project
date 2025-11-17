from flask import Flask, render_template, request, redirect, url_for
import sympy as sp
import numpy as np
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ode_solver.solver import ODESolver
from ode_solver.parser import parse_ode

app = Flask(__name__)

def format_expression(expr):
    """
    Convert SymPy expression to readable, code, and LaTeX formats.
    Returns dict with 'readable', 'code', and 'latex' keys.
    """
    if expr is None:
        return {'readable': '', 'code': '', 'latex': ''}
    try:
        # Readable format: use pretty printing with single-line mode
        readable = sp.pretty(expr, use_unicode=False)
        code = str(expr)
        latex = sp.latex(expr)
        return {'readable': readable, 'code': code, 'latex': latex}
    except:
        expr_str = str(expr)
        return {'readable': expr_str, 'code': expr_str, 'latex': expr_str}

@app.route('/', methods=['GET', 'POST'])
def index():
    solution_img = None
    error = None
    ode_details = None
    if request.method == 'POST':
        ode_str = request.form.get('ode_input', '').strip()
        if not ode_str:
            error = 'Please enter an ODE.'
        else:
            try:
                ode_str_display = ode_str  # Save for UI display
                # Parse ODE using the parser utility
                ode_expr, x, y = parse_ode(ode_str)
                solver = ODESolver(ode_expr, y, x)
                # --- ODE Analysis ---
                analysis = solver.analyze()
                ode_details = {
                    'parsed_ode': format_expression(ode_expr),
                    'order': analysis.get('order'),
                    'is_linear': analysis.get('is_linear'),
                    'coeff_type': None,
                    'aux_eq': None,
                    'roots': None,
                    'root_types': None,
                    'error': None
                }
                if analysis['is_linear']:
                    is_const_coeff = solver.is_constant_coefficient()
                    ode_details['coeff_type'] = 'CONSTANT' if is_const_coeff else 'VARIABLE'
                    if is_const_coeff:
                        try:
                            aux_eq, roots = solver.solve_auxiliary()
                            ode_details['aux_eq'] = format_expression(aux_eq) if aux_eq is not None else None
                            ode_details['roots'] = str(roots) if roots is not None else None
                            try:
                                root_types = solver.classify_roots()
                                ode_details['root_types'] = root_types
                            except Exception:
                                ode_details['root_types'] = None
                        except Exception as e:
                            ode_details['aux_eq'] = None
                            ode_details['roots'] = None
                            ode_details['root_types'] = None
                # --- Solution ---
                sol_analytical = solver.general_solution()
                if sol_analytical is not None:
                    rhs = sol_analytical.rhs
                    constants = [s for s in rhs.free_symbols if s.name.startswith('C')]
                    subs = {c: 1 if i == 0 else 0 for i, c in enumerate(constants)}
                    rhs_num = rhs.subs(subs)
                    f_lambdified = sp.lambdify(x, rhs_num, modules=['numpy'])

                    x_common = np.linspace(-10, 10, 400)
                    try:
                        y_try = f_lambdified(x_common)
                    except Exception:
                        y_list = []
                        for xv in x_common:
                            try:
                                y_list.append(float(f_lambdified(xv)))
                            except Exception:
                                y_list.append(np.nan)
                        y_try = np.array(y_list, dtype=float)

                    if np.isscalar(y_try) or (hasattr(y_try, 'shape') and y_try.shape == ()): 
                        y_vals = np.full_like(x_common, float(y_try), dtype=float)
                    else:
                        y_vals = np.array(y_try, dtype=float)

                    y_vals = np.where(np.isfinite(y_vals), y_vals, np.nan)

                    fig, ax = plt.subplots(figsize=(8,5))
                    ax.plot(x_common, y_vals, label="y(x)")
                    ax.set_title("ODE Solution (Analytical)")
                    ax.set_xlabel("x")
                    ax.set_ylabel("y(x)")
                    ax.legend()
                    ax.grid(True)
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png')
                    buf.seek(0)
                    solution_img = base64.b64encode(buf.read()).decode('utf-8')
                    plt.close(fig)
                    ode_details['solution_type'] = 'Analytical'
                    ode_details['solution_expr'] = format_expression(sol_analytical)
                else:
                    x_vals, y_vals = solver.numerical_solution(x0=0, y0=None, x_span=(-10, 10))
                    if x_vals is not None and y_vals is not None:
                        fig, ax = plt.subplots(figsize=(8,5))
                        ax.plot(x_vals, y_vals, label="y(x)")
                        ax.set_title("ODE Solution (Numerical)")
                        ax.set_xlabel("x")
                        ax.set_ylabel("y(x)")
                        ax.legend()
                        ax.grid(True)
                        buf = io.BytesIO()
                        plt.savefig(buf, format='png')
                        buf.seek(0)
                        solution_img = base64.b64encode(buf.read()).decode('utf-8')
                        plt.close(fig)
                        ode_details['solution_type'] = 'Numerical'
                        ode_details['solution_expr'] = None
                    else:
                        error = 'Unable to solve the ODE analytically or numerically.'
                        ode_details['error'] = error
            except Exception as e:
                error = f'Error: {e}'
    return render_template('index.html', solution_img=solution_img, error=error, ode_details=ode_details)

if __name__ == '__main__':
    app.run(debug=True)
