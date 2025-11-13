"""
Visualization utilities for ODE solutions
"""
import matplotlib.pyplot as plt

def plot_solution(x_vals, y_vals, title="ODE Solution", xlabel="x", ylabel="y(x)"):
    """
    Plots the solution of an ODE.
    Args:
        x_vals (array-like): The x values (independent variable).
        y_vals (array-like): The y values (dependent variable, solution of ODE).
        title (str): Title of the plot.
        xlabel (str): Label for the x-axis.
        ylabel (str): Label for the y-axis.
    Displays the plot using matplotlib.
    """
    plt.figure(figsize=(8, 5))
    plt.plot(x_vals, y_vals, label="y(x)")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.show()
