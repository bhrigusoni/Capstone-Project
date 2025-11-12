"""
Visualization utilities for ODE solutions
"""
import matplotlib.pyplot as plt

def plot_solution(x_vals, y_vals, title="ODE Solution", xlabel="x", ylabel="y"):
    plt.figure(figsize=(8, 5))
    plt.plot(x_vals, y_vals, label="Solution")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.show()
