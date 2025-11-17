# ODE Solver - Pseudocode & Algorithms for Presentation

## 1. Main ODE Solving Algorithm

### High-Level Algorithm: solve(ode_input)
```
ALGORITHM SolveODE(ode_string)
INPUT: ODE as string (e.g., "y'' - 3*y' + 2*y = 0")
OUTPUT: Solution object with general_solution, particular_solution, plot

STEP 1: Parse and Analyze ODE
  - Preprocess input (insert missing multiplication signs)
  - Extract order (highest derivative)
  - Classify as linear or non-linear
  - Separate homogeneous and non-homogeneous parts

STEP 2: If Linear Constant-Coefficient ODE
  - Create auxiliary equation
  - Solve auxiliary equation for roots
  - Classify root types (real, complex, repeated)
  - Construct general solution using root types
  RETURN analytical solution with confidence HIGH

STEP 2b: Else If Linear Euler–Cauchy ODE
  - Detect Euler–Cauchy form (a_k * x^k * y^(k))
  - Extract constant coefficients a_k via robust symbolic substitution
  - Build characteristic equation using falling factorial
  - Solve for roots in r
  - Construct general solution with x^r terms and ln(x) for multiplicities
  RETURN analytical solution with confidence HIGH

STEP 3: Else (Non-linear ODE)
  - TRY: Analytical method specific to ODE type
  - IF successful RETURN analytical solution
  - ELSE: Proceed to numerical method

STEP 4: If Numerical Fallback Needed
  - Convert ODE to system of first-order ODEs
  - Use scipy.integrate.odeint (RK45 method)
  - Evaluate over domain [-10, 10]
  - RETURN numerical solution with confidence MEDIUM

STEP 5: Generate Visualization
  - Create plot of solution curve
  - Encode as base64 image
  - Return to UI

END ALGORITHM
```

---

## 9. Main Solver Class Structure

### Algorithm: create_auxiliary_equation(ode, order)
```
ALGORITHM CreateAuxiliaryEquation(linear_ode, order)
INPUT: Linear ODE, ODE order
OUTPUT: Auxiliary equation (characteristic equation)

PURPOSE: For y'' + a*y' + b*y = 0, create r^2 + a*r + b = 0

STEP 1: Extract Homogeneous Part
  - Remove non-homogeneous terms from ODE
  - Keep only terms with y, y', y'', etc.

STEP 2: Build Characteristic Equation
  FOR each derivative of y:
    - y becomes 1
    - y' becomes r
    - y'' becomes r^2
    - y''' becomes r^3
    - Substitute into homogeneous equation

STEP 3: Simplify and Return
  - Collect coefficients
  - Return as polynomial in r

END ALGORITHM

EXAMPLE:
Input ODE: y'' - 3*y' + 2*y = 0
Step 1: Homogeneous = y'' - 3*y' + 2*y
Step 2: Substitute: r^2 - 3*r + 2 = 0
Output: r^2 - 3*r + 2 = 0
```

---

## 2b. Euler–Cauchy (Equidimensional) Method (Linear Variable-Coefficient ODEs)

### Algorithm: is_euler_cauchy(ode) and solve_euler_cauchy(ode, order)
```
ALGORITHM IsEulerCauchy(linear_ode)
INPUT: Linear ODE
OUTPUT: (True, [a_0, a_1, ..., a_n]) if Euler–Cauchy, else (False, None)

PURPOSE: Detect and extract coefficients from x^k*y^(k) terms

STEP 1: Identify Homogeneous Part
  - Extract homogeneous terms (those with y or derivatives)

STEP 2: For Each Derivative Order k
  - Use robust substitution: replace y^(k) with temporary symbol _tmp_k
  - Extract coefficient of _tmp_k
  - Divide coefficient by x^k to get constant a_k
  - If coefficient is not proportional to x^k, return (False, None)

STEP 3: Validate and Return
  - All a_k must be constants (independent of x)
  - RETURN (True, [a_0, a_1, ..., a_n])

END ALGORITHM

ALGORITHM SolveEulerCauchy(coefficients, order)
INPUT: Constant coefficients [a_0, a_1, ..., a_n], ODE order
OUTPUT: Characteristic equation and roots

PURPOSE: Build characteristic polynomial from Euler–Cauchy form

STEP 1: Build Characteristic Polynomial
  - Use falling factorial: falling_factorial(r, k) = r(r-1)(r-2)...(r-k+1)
  - characteristic_eq = Σ_{k=0..n} a_k * falling_factorial(r, k)

STEP 2: Solve for Roots
  - Solve characteristic_eq = 0 for r

STEP 3: Construct General Solution
  FOR each root r_i with multiplicity m_i:
    IF r_i is real:
      - If m_i = 1: add C*x^(r_i) term
      - If m_i > 1: add (C_1 + C_2*ln(x) + ... + C_m*(ln x)^(m-1))*x^(r_i)
    
    ELSE (complex r_i = a + bi):
      - add x^a * (C_1*cos(b*ln(x)) + C_2*sin(b*ln(x)))

RETURN general_solution

END ALGORITHM

EXAMPLE:
Input ODE: x^2*y'' + x*y' + y = 0
Step 1: Coefficients: a_0=1, a_1=1, a_2=1
Step 2: Characteristic = 1*(1) + 1*r + 1*r(r-1) = 1 + r + r^2 - r = r^2 + 1
Step 3: Solve r^2 + 1 = 0 → r = ±i
Output: y(x) = C_1*cos(ln x) + C_2*sin(ln x)
```

---

## 3. Root Classification Algorithm

### Algorithm: classify_roots(roots)
```
ALGORITHM ClassifyRoots(roots_list)
INPUT: List of roots from auxiliary equation
OUTPUT: Classified roots with their types

STRUCTURE:
- Root = {value, multiplicity, type}
- Type ∈ {REAL_DISTINCT, REAL_REPEATED, COMPLEX_CONJUGATE}

FOR each unique root value:
  STEP 1: Check if real or complex
    IF root is real:
      STEP 2a: Check multiplicity
        IF multiplicity = 1: type = REAL_DISTINCT
        ELSE: type = REAL_REPEATED(multiplicity)
        
        STEP 2b: Contribution to solution
          IF multiplicity = 1: add e^(r*x) to solution
          IF multiplicity = 2: add x*e^(r*x) to solution
          IF multiplicity = 3: add x^2*e^(r*x) to solution
    
    ELSE (complex root): 
      STEP 2a: Extract real and imaginary parts
        root = a + bi
      STEP 2b: Type = COMPLEX_CONJUGATE
      STEP 2c: Contribution to solution
        add e^(a*x)*(C1*cos(b*x) + C2*sin(b*x))

RETURN classified_roots_dict

END ALGORITHM

EXAMPLE OUTPUTS:
1. Roots: [1, 2] → 2 real distinct → Solution: C1*e^x + C2*e^(2x)
2. Roots: [2, 2] → 1 real repeated(2) → Solution: (C1 + C2*x)*e^(2x)
3. Roots: [1+2i, 1-2i] → Complex conjugate → Solution: e^x*(C1*cos(2x) + C2*sin(2x))
```

---

## 4. General Solution Construction

### Algorithm: general_solution(root_classification)
```
ALGORITHM ConstructGeneralSolution(classified_roots)
INPUT: Classified roots from algorithm 3
OUTPUT: General solution formula

PSEUDOCODE:
solution_terms = []

FOR each classified root in classified_roots:
  IF type = REAL_DISTINCT with value r:
    ADD: C_i * e^(r*x) to solution_terms
    
  IF type = REAL_REPEATED with value r, multiplicity m:
    FOR k = 0 to m-1:
      ADD: C_(i+k) * x^k * e^(r*x) to solution_terms
    
  IF type = COMPLEX_CONJUGATE with value a±bi:
    ADD: e^(a*x) * (C_i*cos(b*x) + C_(i+1)*sin(b*x)) to solution_terms

general_solution = SUM(solution_terms)

RETURN general_solution as SymPy expression

END ALGORITHM

CONSTANTS: C1, C2, C3, ... (arbitrary constants)
```

---

## 5. Numerical Solution Method

### Algorithm: numerical_solve(ode_equation, order)
```
ALGORITHM NumericalSolve(ode_equation, order)
INPUT: ODE equation, ODE order
OUTPUT: Numerical solution array

STEP 1: Convert to First-Order System
  IF order = 1:
    y1' = f(x, y1)
    Use ODE directly
  
  ELSE IF order = 2:
    y1 = y, y2 = y'
    y1' = y2
    y2' = f(x, y1, y2)  [from original ODE]
  
  ELSE IF order = n:
    y1 = y, y2 = y', ..., yn = y^(n-1)
    y1' = y2
    y2' = y3
    ...
    yn' = f(x, y1, y2, ..., yn)

STEP 2: Define Initial Conditions
  - For unknown initial conditions: use [1, 0, 0, ...]
  - Represents y(0)=1, y'(0)=0, y''(0)=0, etc.

STEP 3: Setup Solving Parameters
  x_span = [-10, 10]  (domain)
  num_points = 500    (resolution)

STEP 4: Apply Numerical Integration
  solution = scipy.integrate.odeint(system, initial_conditions, x_span)
  Method: RK45 (Runge-Kutta 4th/5th order)

STEP 5: Extract and Return Solution
  Extract y values from solution array
  RETURN (x_array, y_array)

END ALGORITHM

TIME COMPLEXITY: O(n*m) where n = order, m = num_points
SPACE COMPLEXITY: O(m) for storing solution
```

---

## 6. ODE Type Classification

### Algorithm: classify_ode(ode_equation)
```
ALGORITHM ClassifyODE(ode_equation)
INPUT: Parsed ODE equation
OUTPUT: Classification object {order, type, is_linear}

STEP 1: Extract Order
  order = max_derivative_count
  - Check y, y', y'', y''', ...
  - RETURN order

STEP 2: Check Linearity
  linear_check = TRUE
  FOR each term in ODE:
    IF term contains y with power > 1:
      linear_check = FALSE
    IF term contains product of y terms:
      linear_check = FALSE
    IF term contains nonlinear functions like sin(y), e^y:
      linear_check = FALSE
  
  is_linear = linear_check

STEP 3: Check Coefficient Type (if linear)
  is_constant = TRUE
  FOR each derivative term in ODE:
    IF coefficient depends on x:
      is_constant = FALSE
  
  coeff_type = CONSTANT if is_constant else VARIABLE

STEP 4: Classify Type
  IF is_linear and is_constant:
    type = "LINEAR_CONSTANT_COEFFICIENT"
    → Use auxiliary equation method
  
  ELSE IF is_linear and not is_constant:
    IF ODE matches Euler–Cauchy form (a_k * x^k * y^(k)):
      type = "LINEAR_EULER_CAUCHY"
      → Use Euler–Cauchy method
    ELSE:
      type = "LINEAR_VARIABLE_COEFFICIENT"
      → Use numerical method
  
  ELSE:
    Identify special forms:
    IF form matches Riccati: type = "RICCATI"
    IF form matches Bernoulli: type = "BERNOULLI"
    IF form matches Duffing: type = "DUFFING"
    ELSE: type = "GENERAL_NONLINEAR"

STEP 5: Return Classification
  RETURN {order, type, is_linear, is_constant, coeff_type}

END ALGORITHM
```

---

## 7. Expression Formatting

### Algorithm: format_expression(expression)
```
ALGORITHM FormatExpression(sympy_expression)
INPUT: SymPy expression object
OUTPUT: Dictionary with 3 formats

STEP 1: Readable Format
  readable = sp.pretty(expression, use_unicode=False)
  - Uses ASCII art for fractions, exponents, etc.
  - Example: (x + 1)
            -------
              x - 1

STEP 2: Code Format
  code = str(expression)
  - Direct Python/SymPy string representation
  - Example: (x + 1)/(x - 1)

STEP 3: LaTeX Format
  latex = sp.latex(expression)
  - Mathematical typesetting format
  - Example: \frac{x + 1}{x - 1}

STEP 4: Return All Formats
  RETURN {
    'readable': readable,
    'code': code,
    'latex': latex
  }

END ALGORITHM

PURPOSE: Allows users to choose format based on use case
- Readable: For human consumption
- Code: For implementation/documentation
- LaTeX: For academic papers/presentations
```

---

## 8. ODE Solving with Robust Error Handling

### Algorithm: general_solution_with_normalization(ode_expr)
```
ALGORITHM GeneralSolutionWithNormalization(ode_expr)
INPUT: SymPy ODE expression
OUTPUT: Solution Eq object or None

PURPOSE: Attempt analytical solution, normalize multi-solution outputs, handle edge cases

STEP 1: Call SymPy dsolve
  TRY:
    sol = sp.dsolve(ode_expr)
  CATCH Exception:
    RETURN None

STEP 2: Normalize Output
  IF sol is a list or tuple:
    - Check for Eq-like solutions (with .rhs attribute)
    - Pick the first Eq-like solution
    - IF no Eq found, RETURN None
  
  IF sol does not have .rhs:
    - Unsupported return type
    - RETURN None

STEP 3: Return Valid Solution
  IF sol has .rhs:
    RETURN sol
  ELSE:
    RETURN None

END ALGORITHM

PURPOSE: Some nonlinear ODEs return multiple solutions or non-Eq objects. This normalizes the output to prevent downstream errors like "'list' object has no attribute 'rhs'".

EXAMPLE:
Input: y'**2 = x (nonlinear)
dsolve returns: [Eq(...), Eq(...)] or unwrapped expression
Output: First Eq object or None if not found
```

### Pseudocode: ODESolver Class
```
CLASS ODESolver:
  
  ATTRIBUTES:
    - ode_string: Original ODE input
    - ode_equation: Parsed SymPy equation
    - x: SymPy symbol for independent variable
    - y: SymPy function object
    - order: ODE order
    - is_linear: Boolean
    - is_constant_coefficient: Boolean
    - auxiliary_eq: Characteristic equation (if linear)
    - roots: List of roots
    - general_solution: Solution formula
    - particular_solution: Solution with initial conditions
    - confidence: ANALYTICAL or NUMERICAL or ERROR
  
  METHODS:
    
    __init__(ode_string)
      - Parse ODE
      - Initialize attributes
    
    analyze()
      - Determine order, type, linearity
      - Call appropriate solving method
    
    solve_auxiliary()
      - Create auxiliary equation
      - Solve for roots
    
    classify_roots()
      - Categorize root types
      - Construct solution formula
    
    general_solution()
      - Combine root types into formula
      - Add arbitrary constants
    
    numerical_solution()
      - Convert to first-order system
      - Use scipy.integrate.odeint
      - Return numerical array
    
    create_first_order_system()
      - Convert nth order to n first-order equations
      - Define system for scipy
    
    generate_plot()
      - Plot solution curve
      - Return matplotlib figure

END CLASS
```

---

## 9. Error Handling & Edge Cases

### Algorithm: validate_and_solve(ode_input)
```
ALGORITHM ValidateAndSolve(ode_input)

TRY:
  STEP 1: Input Validation
    IF ode_input is empty:
      THROW ValueError("Empty ODE")
    IF ode_input length > 1000:
      THROW ValueError("ODE too long")
  
  STEP 2: Preprocess
    ode_input = preprocess_input(ode_input)
    - Insert missing * signs
    - Normalize whitespace

  STEP 3: Parse
    ode_equation = sp.Eq(...)
    - Try to parse as SymPy equation
    IF parsing fails:
      THROW SyntaxError("Invalid ODE syntax")

  STEP 4: Analyze & Solve
    solver = ODESolver(ode_string)
    result = solver.analyze()

  STEP 5: Return Result
    RETURN result

CATCH ParseError:
  RETURN error_message with suggestion

CATCH TimeoutError:
  RETURN "Solving took too long, using numerical method..."
  result = numerical_solve()
  RETURN result

CATCH Exception:
  LOG error
  RETURN generic error message

END ALGORITHM
```

---

## 10. Complete Flowchart

```
START
  |
  v
INPUT: ODE String
  |
  v
PREPROCESS (add * signs, normalize)
  |
  v
PARSE to SymPy Equation
  | 
  +--[Parse Error?]--YES--> ERROR: Invalid Syntax
  |
  NO
  v
ANALYZE ODE
  |
  +--[Extract Order, Type, Linearity]
  |
  v
IS LINEAR?
  |
  +--YES--> IS CONSTANT COEFFICIENT?
  |           |
  |           +--YES--> CREATE AUXILIARY EQUATION
  |           |           |
  |           |           v
  |           |        SOLVE AUXILIARY (find roots)
  |           |           |
  |           |           v
  |           |        CLASSIFY ROOTS
  |           |           |
  |           |           v
  |           |        BUILD GENERAL SOLUTION
  |           |           |
  |           +--NO---> CHECK FOR EULER-CAUCHY FORM
  |                       |
  |                       +--YES--> EXTRACT COEFFICIENTS (a_0, ..., a_n)
  |                       |           |
  |                       |           v
  |                       |        BUILD CHARACTERISTIC EQ (falling factorial)
  |                       |           |
  |                       |           v
  |                       |        SOLVE FOR ROOTS (in r)
  |                       |           |
  |                       |           v
  |                       |        BUILD GENERAL SOLUTION (x^r terms)
  |                       |
  |                       +--NO---> USE NUMERICAL METHOD
  |
  +--NO (Non-linear) --> TRY ANALYTICAL METHOD
                           |
                           +--[Success?]--YES--> RETURN SOLUTION
                           |
                           NO
                           |
                           v
                        USE NUMERICAL METHOD
                           |
                           v
SOLVE NUMERICALLY (odeint)
  |
  v
GENERATE VISUALIZATION
  |
  v
FORMAT EXPRESSIONS (Readable/Code/LaTeX)
  |
  v
RETURN: {solution, plot, analysis}
  |
  v
END
```

---

## Key Points for Presentation

1. **Triple-Layer Approach**: Auxiliary equations for constant-coefficient, Euler–Cauchy for variable-coefficient, numerical fallback
2. **Euler–Cauchy Support**: Key innovation — handles equidimensional ODEs with characteristic equation method
3. **Robust Preprocessing**: Smart handling of omitted multiplication, various notation styles
4. **Root Classification**: Different solution forms for distinct, repeated, and complex root types
5. **Multi-Format Output**: Flexibility for different use cases (readable, code, LaTeX)
6. **Graceful Error Handling**: Robust normalization of SymPy outputs, domain-aware visualization
7. **User Experience**: Clean web interface, domain masking for invalid points (log, fractional powers)
8. **Mathematical Rigor**: Based on standard differential equations theory, verified examples
