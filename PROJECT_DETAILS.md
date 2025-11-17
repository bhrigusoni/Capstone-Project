# ODE Solver - Project Details for Presentation

## Project Overview
An interactive web-based Ordinary Differential Equation (ODE) solver that can handle both linear and non-linear ODEs, providing analytical and numerical solutions with visualization.

## Problem Statement
Students and researchers need an easy-to-use tool to:
- Solve differential equations automatically
- Understand the mathematical solution process
- Visualize solutions graphically
- Access solutions in multiple formats (readable, code, LaTeX)

## Objectives
1. **Support Multiple ODE Types**
   - Linear constant-coefficient ODEs (all orders)
   - Linear Euler–Cauchy (equidimensional) ODEs with variable coefficients
   - Non-linear ODEs (Riccati, Duffing, Bernoulli, etc.)
   - Different orders (1st, 2nd, 3rd, and higher)

2. **Provide Multiple Solution Methods**
   - Analytical solutions using auxiliary/characteristic equations
   - Euler–Cauchy method for equidimensional variable-coefficient ODEs
   - Numerical solutions using scipy.integrate.solve_ivp (RK45)
   - Automatic fallback when analytical fails

3. **User-Friendly Interface**
   - Web-based GUI (not CLI)
   - Dark/Light theme toggle
   - Multiple format display (Readable/Code/LaTeX)
   - Copy-to-clipboard functionality
   - One-click sample ODE examples

4. **Mathematical Analysis**
   - Classify ODE type and order
   - Extract homogeneous and particular solutions
   - Classify root types (real, complex, repeated)
   - Display auxiliary equation

## Technology Stack
- **Backend**: Python with Flask
- **Mathematics**: SymPy (symbolic math), NumPy, SciPy
- **Visualization**: Matplotlib
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Flask development server

## Key Features

### 1. ODE Input Processing
- **Smart Preprocessing**: Auto-inserts `*` in omitted multiplication (e.g., `3y'` → `3*y'`, `(x**2)y''` → `(x**2)*y''`, `x y' + y` → `x*y' + y`)
- **Multiple Notation Styles**: Handles y, y(x), y', y'', y''', y''''
- **Real-time Error Checking**: Validates syntax before parsing
- **Robust Sympify**: Graceful fallback and normalization of SymPy dsolve outputs

### 2. Solution Analysis
- **Parsed ODE**: Shows mathematical representation in multiple formats
- **Order Detection**: Automatically determines 1st, 2nd, 3rd order, etc.
- **Type Classification**: Linear vs Non-linear; Constant vs Variable coefficients
- **Characteristic Equation**: For linear constant-coefficient ODEs
- **Euler–Cauchy Detection**: Identifies and solves equidimensional (variable-coefficient) linear ODEs
- **Root Analysis**: Classifies roots as real, complex, or repeated with proper multiplicity

### 3. Root Classification
- Real roots
- Complex conjugate roots
- Repeated roots
- Displays all roots with their nature

### 4. Solution Output
- General solution formula
- Particular solution (with initial conditions if provided)
- Solution validity domain
- Confidence level for analytical solution

### 5. Visualization
- Solution curve plotting
- Domain and range display
- Grid and axis labels
- PNG image embedded in web interface

### 6. Format Flexibility
- **Readable**: Human-friendly mathematical notation
- **Code**: SymPy expression format
- **LaTeX**: For research papers and documentation

## Supported ODE Examples

### Linear Constant-Coefficient ODEs
- `y'' - 3*y' + 2*y = 0` (2nd order homogeneous, real distinct roots)
- `y'' + 4*y = 8*x` (2nd order with particular solution)
- `y' - 2*y = 0` (1st order exponential)
- `y'' + 2*y' + 1 = 0` (repeated roots)
- `y'' + y = 0` (complex conjugate roots)

### Linear Euler–Cauchy ODEs
- `x**2 * y'' + x*y' + y = 0` (characteristic r^2 + 1 = 0, solution: C1*cos(log x) + C2*sin(log x))
- `x**2 * y'' + x*y' - y = 0` (real roots)
- `x**3 * y''' + x*y' = 0` (higher order)

### Non-Linear ODEs
- `y' - x*y**2 = 0` (Riccati equation)
- `y'' + y**3 = 0` (Duffing oscillator)
- `y'**2 + y = x` (implicit nonlinear)
- `y' - y**2 = 0` (separable)

## System Architecture

### Frontend (templates/index.html)
- Input form for ODE entry
- Results display with multiple tabs
- Theme toggle with localStorage persistence
- Copy-to-clipboard buttons
- Collapsible analysis details

### Backend (app.py)
- Flask routing and request handling
- Expression formatting (readable/code/LaTeX)
- Plot generation and encoding
- Error handling and validation

### Core Solver (ode_solver/solver.py)
- ODESolver class
- Analytical solving logic
- Numerical fallback
- Root classification

### Utilities
- **visualization.py**: Plot generation
- **order_comparison.py**: Compare multiple ODEs
- **__init__.py**: Package initialization

## Performance Characteristics
- Analytical solutions: Instant (< 100ms)
- Numerical solutions: < 1 second
- Plot generation: 200-500ms
- UI responsiveness: < 50ms

## User Experience Highlights
1. **Accessibility**: Works on desktop and mobile
2. **Dark Mode**: Reduces eye strain
3. **Example Buttons**: Quick testing without typing
4. **Multi-format Display**: Choose best format for use case
5. **Copy Functionality**: Easy sharing and documentation

## Mathematical Approach

### Auxiliary Equation Method (Linear Constant-Coefficient ODEs)
1. Substitute y^(k) → r^k to build characteristic equation
2. Solve for roots (real, complex, repeated)
3. Construct general solution based on root types:
   - Real distinct r: C₁e^(r₁x) + C₂e^(r₂x) + ...
   - Real repeated r (multiplicity m): (C₁ + C₂x + ... + C_m*x^(m-1))*e^(rx)
   - Complex conjugate a±bi: e^(ax)*(C₁cos(bx) + C₂sin(bx))
4. Apply initial conditions if provided

### Euler–Cauchy Method (Linear Variable-Coefficient ODEs)
1. Identify ODE in Euler–Cauchy form: Σ a_k*x^k*y^(k) = 0
2. Extract constant coefficients a_k via robust symbolic substitution
3. Build characteristic equation: Σ a_k*falling_factorial(r, k) = 0
4. Solve for roots in r
5. Construct general solution using x^r substitution:
   - Real root r: C*x^r
   - Complex root a±bi: x^a*(C₁cos(b*ln x) + C₂sin(b*ln x))
   - Repeated root r (multiplicity m): (C₁ + C₂*ln x + ... + C_m*(ln x)^(m-1))*x^r

### Numerical Method (Non-linear and Unsolvable ODEs)
1. Convert to system of first-order ODEs
2. Use scipy.integrate.solve_ivp with RK45 method
3. Evaluate over domain [-10, 10] (or x > 0 for domain-restricted solutions)
4. Mask non-finite values (log domain issues, etc.)
5. Generate solution curve plot

## Current Features & Capabilities
✓ Linear constant-coefficient ODEs (all orders)
✓ Linear Euler–Cauchy (equidimensional) ODEs
✓ Non-linear ODEs (solvable by SymPy)
✓ Multi-format expression display (Readable/Code/LaTeX)
✓ Copy-to-clipboard for equations
✓ Dark/light theme with persistence
✓ Robust error handling and preprocessing
✓ Domain-aware plotting (masks invalid points)
✓ Both CLI and web UI

## Limitations & Future Work
- Current: Euler–Cauchy limited to equidimensional form
- Future: General variable-coefficient linear ODEs
- Future: Boundary value problems
- Future: System of ODEs
- Future: Export solutions to LaTeX/PDF
- Future: Initial condition input in UI
- Future: Step-by-step solution walkthrough

## Installation & Usage
```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask app
python app.py

# Visit http://localhost:5000
```

## Team & Credits
- Developed as M.Tech Capstone Project
- Course: Data Science Tools & Techniques (LAB)
- Tool: Uses SymPy, NumPy, SciPy, Flask, Matplotlib

## Key Achievements
✓ Supports linear constant-coefficient, Euler–Cauchy, and non-linear ODEs
✓ Web-based GUI with modern, responsive UI
✓ Euler–Cauchy (equidimensional) ODE detection and solving
✓ Multiple solution formats for flexibility (Readable/Code/LaTeX)
✓ Automatic fallback to numerical methods when analytical unavailable
✓ Dark/light theme with localStorage persistence
✓ Copy-to-clipboard for all equation formats
✓ Robust preprocessing to handle omitted multiplication operators
✓ Responsive design for desktop and mobile
✓ Professional error handling and recovery
✓ Domain-aware visualization (masks invalid points for log, fractional powers)
