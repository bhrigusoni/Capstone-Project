"""
General ODE Solver Core Logic
Supports both Linear and Non-linear ODEs
"""
import sympy as sp
import numpy as np
from scipy.integrate import odeint, solve_ivp
import warnings

class ODESolver:
    def __init__(self, ode_expr, func, var):
        """
        Initialize the ODESolver with a sympy ODE expression, the function (e.g., y), and the variable (e.g., x).
        Stores the ODE, function, and variable for use in other methods.
        """
        self.ode_expr = ode_expr
        self.func = func
        self.var = var
        self.solution = None
        self.solution_type = None  # 'analytical', 'numerical', or 'failed'

    def analyze(self):
        """
        Analyze the ODE to determine its order, linearity, and coefficients.
        - Finds the order using sympy's ode_order.
        - Checks linearity by ensuring each term is linear in y and its derivatives.
        - Attempts to extract coefficients for each derivative using sympy.Poly.
        Returns a dictionary with order, is_linear, and coefficients.
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

    def is_constant_coefficient(self):
        """
        Check if the ODE is a constant-coefficient linear ODE.
        - For each term containing y or its derivatives, checks if the coefficient depends on x.
        - Returns True if all coefficients are constant (do not depend on x), otherwise False.
        """
        analysis = self.analyze()
        if not analysis['is_linear']:
            return False
        
        order = analysis['order']
        y = self.func(self.var)
        x = self.var
        
        # Extract all terms and check coefficients of each derivative
        expr = self.ode_expr.expand()
        terms = expr.as_ordered_terms()
        
        # For each term, extract the derivative it contains (if any)
        # and check if the coefficient depends on x
        for term in terms:
            # Check for each derivative order
            for i in range(order + 1):
                deriv = y.diff(x, i)
                if term.has(deriv):
                    # This term contains this derivative
                    # Extract the coefficient
                    coeff = term.as_coeff_mul(deriv)[0]
                    
                    # Check if coefficient depends on x
                    if coeff.has(x):
                        # Coefficient depends on x -> variable-coefficient
                        return False
        
        return True

    def solve_auxiliary(self):
        """
        Construct and solve the auxiliary (characteristic) equation for constant-coefficient linear ODEs.
        - Only applies if the ODE is linear and has constant coefficients.
        - Substitutes y^(n) with r^n, y' with r, y with 1 in the homogeneous part.
        - Returns the auxiliary equation and its roots, or (None, None) if not applicable.
        """
        analysis = self.analyze()
        if not analysis['is_linear']:
            return None, None
        
        # Check if it's constant-coefficient
        if not self.is_constant_coefficient():
            return None, None  # Variable-coefficient linear ODE
        
        order = analysis['order']
        y = self.func(self.var)
        r = sp.symbols('r')

        # Get the homogeneous part: move all terms to one side, set equal to zero
        # If the ODE is of the form LHS = RHS, we want LHS - RHS = 0
        # Assume ode_expr is always LHS - RHS (as per sympy Eq convention)
        # If it's an Eq, get lhs - rhs; else, use as is
        expr = self.ode_expr
        if isinstance(expr, sp.Equality):
            hom_expr = expr.lhs - expr.rhs
        else:
            hom_expr = expr

        # Remove non-homogeneous terms (those not involving y or its derivatives)
        # Only keep terms with y or its derivatives
        derivs = [y.diff(self.var, i) for i in range(order + 1)]
        hom_terms = []
        for term in hom_expr.expand().as_ordered_terms():
            if any(term.has(d) for d in derivs):
                hom_terms.append(term)
        hom_expr = sum(hom_terms)

        # Build auxiliary equation: replace y^(n) with r^n, y' with r, y with 1
        aux_eq = hom_expr
        for i in range(order, 0, -1):
            aux_eq = aux_eq.subs(y.diff(self.var, i), r**i)
        aux_eq = aux_eq.subs(y, 1)
        aux_eq = sp.simplify(aux_eq)
        
        try:
            roots = sp.solve(aux_eq, r)
        except:
            roots = []
        
        return aux_eq, roots

    def classify_roots(self):
        """
        Classify the roots of the auxiliary equation.
        - Separates roots into real, complex, and repeated categories.
        - Returns a dictionary with lists of real, complex, and repeated roots.
        Returns None if roots are not available.
        """
        _, roots = self.solve_auxiliary()
        if roots is None or len(roots) == 0:
            return None
        
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
        Attempt to find the general analytic solution using sympy's dsolve.
        - If successful, stores and returns the solution.
        - If not, marks the solution type as 'numerical' and returns None.
        """
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                sol = sp.dsolve(self.ode_expr, self.func(self.var))
            self.solution = sol
            self.solution_type = 'analytical'
            return sol
        except Exception as e:
            print(f"\nNote: Analytical solution not available.")
            print(f"Reason: {str(e)[:100]}")
            self.solution_type = 'numerical'
            return None

    def numerical_solution(self, x0=0, y0=None, x_span=(-10, 10), dense_output=True):
        """
        Numerically solve the ODE using scipy's solve_ivp.
        - Converts the ODE to a first-order system if needed.
        - Uses default initial conditions if not provided.
        - Returns arrays of x and y values if successful, otherwise (None, None).
        """
        analysis = self.analyze()
        order = analysis['order']
        
        if y0 is None:
            # Default initial conditions
            y0 = [1.0] + [0.0] * (order - 1)
        
        if len(y0) != order:
            raise ValueError(f"Expected {order} initial conditions, got {len(y0)}")
        
        # Convert ODE to first-order system
        # For an ODE of order n, create n first-order ODEs
        try:
            system_func = self._create_first_order_system()
            
            # Use solve_ivp for better handling of stiff and non-linear systems
            t_eval = np.linspace(x_span[0], x_span[1], 400)
            
            sol = solve_ivp(
                system_func,
                (x_span[0], x_span[1]),
                y0,
                t_eval=t_eval,
                method='RK45',
                dense_output=True,
                max_step=0.1
            )
            
            if sol.status == 0:  # Successful integration
                self.solution = sol
                self.solution_type = 'numerical'
                return sol.t, sol.y[0]  # Return x values and first component (y)
            else:
                print(f"Numerical integration failed: {sol.message}")
                return None, None
                
        except Exception as e:
            print(f"Error in numerical solution: {str(e)[:200]}")
            return None, None

    def _create_first_order_system(self):
        """
        Convert the ODE to a system of first-order ODEs for numerical integration.
        - Expresses the ODE as a system suitable for scipy's ODE solvers.
        - Returns a function that computes derivatives for the system.
        """
        analysis = self.analyze()
        order = analysis['order']
        y = self.func(self.var)
        x = self.var
        
        # For a single ODE, we need to convert it to first-order system
        # u[0] = y, u[1] = y', u[2] = y'', etc.
        # du[0]/dx = u[1]
        # du[1]/dx = u[2]
        # ...
        # du[n-1]/dx = (solve for highest derivative from ODE)
        
        # Create symbols for the derivatives
        derivs = [y.diff(x, i) for i in range(order)]
        
        # Solve ODE for the highest derivative
        highest_deriv = y.diff(x, order)
        try:
            highest_deriv_expr = sp.solve(self.ode_expr, highest_deriv)[0]
        except:
            # If can't solve explicitly, return a function that will fail gracefully
            def system(x_val, u):
                return [u[i] if i < len(u) - 1 else 0 for i in range(len(u))]
            return system
        
        # Create lambda function for the highest derivative
        # Need to substitute u[i] for y^(i)
        # Build a dict for substitution
        lambdify_args = [x]
        subs_dict = {}
        for i, d in enumerate(derivs):
            subs_dict[d] = sp.symbols(f'u_{i}')
            lambdify_args.append(subs_dict[d])
        
        # Substitute in the expression
        expr_substituted = highest_deriv_expr.subs(subs_dict)
        
        # Create lambda function
        lambda_func = sp.lambdify(
            tuple(lambdify_args),
            expr_substituted,
            modules=['numpy']
        )
        
        def system(x_val, u):
            """
            System of first-order ODEs.
            u[0] = y, u[1] = dy/dx, u[2] = d2y/dx2, etc.
            """
            dudt = np.zeros(len(u))
            for i in range(len(u) - 1):
                dudt[i] = u[i + 1]
            
            try:
                dudt[-1] = lambda_func(x_val, *u)
            except:
                dudt[-1] = 0
            
            return dudt
        
        return system
