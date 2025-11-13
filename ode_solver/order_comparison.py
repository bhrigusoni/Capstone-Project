"""
Order comparison utilities for ODE solutions
"""
import matplotlib.pyplot as plt

def compare_orders(x_vals, solutions, labels=None, title="ODE Order Comparison"):
    """
    Plots and compares solutions of ODEs of different orders on the same graph.
    Args:
        x_vals (array-like): The x values (independent variable).
        solutions (list of array-like): List of y values for each ODE solution.
        labels (list of str, optional): Labels for each solution curve.
        title (str): Title of the plot.
    Displays the plot using matplotlib.
    """
    plt.figure(figsize=(8, 5))
    for i, y_vals in enumerate(solutions):
        label = labels[i] if labels and i < len(labels) else f"Solution {i+1}"
        plt.plot(x_vals, y_vals, label=label)
    plt.title(title)
    plt.xlabel("x")
    plt.ylabel("y(x)")
    plt.legend()
    plt.grid(True)
    plt.show()
