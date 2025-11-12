"""
General ODE Solver Core Logic
"""
import sympy as sp

class ODESolver:
    def __init__(self, ode_expr, func, var):
        self.ode_expr = ode_expr
        self.func = func
        self.var = var

    def analyze(self):
        """
        Analyze the ODE: order, linearity, coefficients, etc.
        Returns a dict with analysis results.
        """
        # Order: highest derivative order
        order = sp.ode_order(self.ode_expr, self.func(self.var))
        # Linearity: check if ODE is linear in the function and its derivatives
        # We'll check linearity by seeing if the ODE is linear in y and its derivatives
        y = self.func(self.var)
        derivs = [y.diff(self.var, i) for i in range(order + 1)]
        # Improved linearity check: only check terms involving y(x) or its derivatives
        expr = self.ode_expr.expand()
        terms = expr.as_ordered_terms()
        def is_term_linear(term):
            # If term does not contain y(x) or its derivatives, it's fine
            if not any(term.has(d) for d in derivs):
                return True
            # Check for products or powers of y(x) or its derivatives
            found = []
            for d in derivs:
                exp = term.as_coeff_exponent(d)[1]
                if exp > 1:
                    return False  # Power > 1
                if term.has(d) and exp == 1:
                    found.append(d)
            # If more than one unique y(x) or derivative appears, it's a product, so nonlinear
            if len(found) > 1:
                return False
            return True
        is_linear = all(is_term_linear(term) for term in terms)
        # Coefficients: extract coefficients for constant-coefficient ODEs
        try:
            # Try to get coefficients for the highest derivative
            poly = sp.Poly(self.ode_expr, *derivs)
            coeffs = poly.coeffs()
        except Exception:
            coeffs = None
        return {
            'order': order,
            'is_linear': is_linear,
            'coefficients': coeffs
        }

    def solve_auxiliary(self):
        """
        Derive and solve the auxiliary (characteristic) equation for constant-coefficient linear ODEs.
        Returns the auxiliary equation and its roots.
        """
        # Only for constant-coefficient linear ODEs
        order = sp.ode_order(self.ode_expr, self.func(self.var))
        y = self.func(self.var)
        r = sp.symbols('r')
        # Build auxiliary equation: replace y^(n) with r^n, y' with r, y with 1
        aux_eq = self.ode_expr
        for i in range(order, 0, -1):
            aux_eq = aux_eq.subs(y.diff(self.var, i), r**i)
        aux_eq = aux_eq.subs(y, 1)
        aux_eq = sp.simplify(aux_eq)
        roots = sp.solve(aux_eq, r)
        return aux_eq, roots

    def classify_roots(self):
        """
        Classify the roots of the auxiliary equation.
        Returns a dict with root types and values.
        """
        _, roots = self.solve_auxiliary()
        real = []
        complex_ = []
        repeated = []
        seen = {}
        for root in roots:
            if sp.im(root) == 0:
                real.append(root)
            else:
                complex_.append(root)
            seen[root] = seen.get(root, 0) + 1
        for root, count in seen.items():
            if count > 1:
                repeated.append(root)
        return {
            'real': real,
            'complex': complex_,
            'repeated': repeated
        }

    def general_solution(self):
        """
        Compute the general analytic solution using sympy's dsolve.
        Returns the general solution.
        """
        sol = sp.dsolve(self.ode_expr, self.func(self.var))
        return sol
