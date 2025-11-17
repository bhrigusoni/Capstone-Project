# QUICK START GUIDE - ODE Solver

## 1. Installation (One-time Setup)
```bash
cd "Capstone Project"
pip install -r requirements.txt
```

## 2. Run the Solver
```bash
python main.py
```

## 3. Enter Your ODE

### Format Options
```
Option A: y'' - 3*y' + 2*y = 0     # Equals form
Option B: y'' - 3*y' + 2*y         # Implicit (= 0)
Option C: y'' = 3*y' - 2*y         # Explicit form
```

### Derivative Notation
- `y` = function value
- `y'` = first derivative (dy/dx)
- `y''` = second derivative (d²y/dx²)
- `y'''` = third derivative
- `y''''` = fourth derivative

## 4. Example Inputs

### LINEAR CONSTANT-COEFFICIENT ODEs
```
y' - y = 0
y'' + 2*y' + y = 0
y'' - 4*y = 0
3*y'' + 5*y' - 2*y = 0
y''' - 2*y'' + y' = 0
```

### LINEAR EULER–CAUCHY (EQUIDIMENSIONAL) ODEs
```
x**2 * y'' + x*y' + y = 0        # Complex roots ±i → cos(ln x), sin(ln x)
x**2 * y'' + x*y' - y = 0        # Real roots → x^r terms
x**3 * y''' + x*y' = 0           # Higher order
(x**2)y'' + xy' = 0              # No constant term
```

### NON-LINEAR ODEs
```
y' = y**2
y' - x*y**2 = 0
y'' + y**3 = 0
y' - y*(1-y) = 0
```

## 5. What the Program Shows

### Analysis Section
```
Order: 1              # 1st, 2nd, 3rd, or 4th order
Is Linear: True       # Linear or Non-linear
Type: LINEAR ODE      # Classification
Coefficient Type: CONSTANT or VARIABLE
```

### For Constant-Coefficient Linear ODEs
```
Auxiliary equation: r^2 - 3*r + 2 = 0
Roots: [1, 2]
Root classification:
  Real roots: [1, 2]
  Complex roots: []
  Repeated roots: []
```

### For Euler–Cauchy Linear ODEs
```
[VARIABLE-COEFFICIENT ODE - Euler-Cauchy detected]
Characteristic equation (in r): r^2 + 1 = 0
Roots (r): [-I, I]  (complex conjugate)
Root classification:
  Real roots: []
  Complex roots: [-I, I]
  Repeated roots: []
```

### Solution
```
[OK] ANALYTICAL SOLUTION FOUND:
y(x) = C1*e^x + C2*e^(2*x)

OR

[INFO] No closed-form solution found.
[OK] NUMERICAL SOLUTION FOUND
(Plot will be displayed)
```

## 6. Solution Types

| When? | What You See |
|-------|-------------|
| Closed-form solution exists | `[OK] ANALYTICAL SOLUTION FOUND` + formula |
| No closed-form but solvable | `[OK] NUMERICAL SOLUTION FOUND` + plot |
| Cannot be solved | `[FAILED] Unable to solve` + suggestions |

## 7. What Constants Mean

### In Constant-Coefficient Linear Solutions
```
y(x) = C1*e^x + C2*e^(2*x)
       ↑  ↑
       |  Arbitrary constant 2
       Arbitrary constant 1
```

### In Euler–Cauchy (Variable-Coefficient) Linear Solutions
```
y(x) = C1*x^(1+i) + C2*x^(1-i)    OR    y(x) = C1*x*cos(ln x) + C2*x*sin(ln x)
       ↑ Power of x with complex r       ↑ x raised to power, times trig function
```

### In Plots
- Constants are set to: C1=1, C2=0, C3=0, etc.
- This gives one specific solution (the principal solution)
- For initial value problems, choose different constants based on initial conditions

## 8. Troubleshooting

| Problem | Solution |
|---------|----------|
| "Error parsing ODE" | Check syntax: y'' means second derivative, use * for multiplication |
| Variable-coefficient ODE not solved | If equidimensional (x^n*y, x*y', etc.), should use Euler–Cauchy method. If still fails, numerical approximation is shown |
| No solution found | Try simpler ODE or check format. Check that x multiplication isn't omitted |
| Plot doesn't appear | Solution may be undefined in [-10,10] (e.g., log domain issues). Try anyway! |
| "Numerical solution failed" | Try simpler initial conditions or try the analytical solver first |
| Solution contains ln(x) terms | Only plotted for x > 0 due to logarithm domain. Plot will show [0.1, 10] range |

## 9. Example Session

```bash
$ python main.py

================================================================================
Welcome to the General ODE Solver!
Enter an ODE: y'' - 3*y' + 2*y = 0

ODE ANALYSIS:
Order: 2
Is Linear: True
Type: LINEAR ODE

LINEAR ODE ANALYSIS:
Auxiliary equation: r^2 - 3*r + 2 = 0
Roots: [1, 2]
Root classification:
  Real roots: [1, 2]
  Complex roots: []
  Repeated roots: []

[OK] ANALYTICAL SOLUTION FOUND:
y(x) = C1 + C2*e^x

VISUALIZATION:
[OK] Plot displayed successfully
```

## 10. Supported Equation Types

### Linear
✓ Homogeneous (RHS = 0)
✓ Non-homogeneous with constant/variable coefficients
✓ 1st to 4th order
✓ With complex roots

### Non-linear
✓ Separable (y' = f(x)*g(y))
✓ Riccati (y' + P(x)*y² = Q(x))
✓ Duffing (y'' + ay + by³ = 0)
✓ Logistic (y' = y*(1-y))
✓ Any equation solvable by SymPy

### Not Supported
✗ Partial differential equations
✗ Systems of ODEs
✗ Functional differential equations
✗ Delay differential equations

## 11. Tips & Tricks

1. **Use brackets for clarity**: `(y')**2` not `y'^2`
2. **Use * for multiplication**: `2*y` not `2y`
3. **Use ** for powers**: `y**2` not `y^2`
4. **Try simpler forms first**: If complex ODE fails, reduce it
5. **Check dimensions**: Make sure equation is balanced

## 12. Feature Comparison

| Feature | Our Solver | SymPy dsolve | SciPy odeint |
|---------|-----------|-------------|-------------|
| Analytical (Linear) | ✓ | ✓ | ✗ |
| Analytical (Non-linear) | ✓ | ✓ | ✗ |
| Numerical solution | ✓ | ✗ | ✓ |
| Auto fallback | ✓ | ✗ | ✗ |
| Visualization | ✓ | ✗ | ✗ |
| Auxiliary equation | ✓ | ✗ | ✗ |
| User-friendly | ✓ | ✗ | ✗ |

## 13. Mathematical Background

### What the solver does:
1. **Parses** your equation using regex patterns to handle omitted multiplication
2. **Analyzes** order (highest derivative), linearity, and coefficient type
3. **Classifies** as one of:
   - Constant-coefficient linear (uses auxiliary equation method)
   - Euler–Cauchy variable-coefficient (uses characteristic equation with falling-factorial substitution)
   - Non-linear (uses SymPy dsolve with numerical fallback)
4. **Solves** using appropriate analytical or numerical method
5. **Substitutes** constants for visualization (C1=1, C2=0, etc.)
6. **Plots** the solution with domain-aware masking for log/power functions

### Example Process (Constant-Coefficient):
```
Input:  y'' - 3*y' + 2*y = 0
Parse:  d²y/dx² - 3·dy/dx + 2·y = 0
Analyze: Order 2, Linear, Constant-coefficient
Solve:  Auxiliary: r² - 3r + 2 = 0 → r = 1, 2
        Solution: y = C1·e^x + C2·e^(2x)
Visualize: Set C1=1, C2=0 → plot e^x
```

### Example Process (Euler–Cauchy):
```
Input:  x^2*y'' + x*y' + y = 0
Parse:  x²·d²y/dx² + x·dy/dx + y = 0
Analyze: Order 2, Linear, Euler–Cauchy (equidimensional)
Solve:  Characteristic: r² + 1 = 0 → r = ±i
        Solution: y = C1·cos(ln x) + C2·sin(ln x)
Visualize: Set C1=1, C2=0 → plot cos(ln x) for x > 0
```

## 14. For Your Project Report

Include:
- Screenshots of successful ODE solutions covering all three types:
  - **Linear Constant-Coefficient**: y'' - 3*y' + 2*y = 0 (real roots)
  - **Linear Euler–Cauchy**: x^2*y'' + x*y' + y = 0 (complex roots → trigonometric solution)
  - **Non-linear**: y' = x + y^2 (numerical solution)
- Output analysis and characteristic/auxiliary equations
- Sample plots generated (both analytical and numerical)
- Comparison of three solver layers (symbolic, Euler–Cauchy, numerical)
- Advantages of the multi-method approach (versatility and reliability)

## 15. Get Help

- Run: `python test_solver.py` to see working examples
- Check: `README.md` for detailed documentation
- Review: `problem.txt` for original requirements
- Examine: `ode_solver/solver.py` for implementation

---

**Ready to solve ODEs?** Run `python main.py` now!
