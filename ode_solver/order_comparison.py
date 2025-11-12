"""
Order comparison utilities for ODE solutions
"""
def compare_orders(solutions, x_vals):
    # solutions: dict of {order: (x_vals, y_vals)}
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8, 5))
    for order, (x, y) in solutions.items():
        plt.plot(x, y, label=f"Order {order}")
    plt.title("Comparison of ODE Solutions by Order")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.grid(True)
    plt.show()
