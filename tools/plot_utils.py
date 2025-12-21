import os
import matplotlib.pyplot as plt

# Configure Matplotlib to display Chinese characters correctly
plt.rcParams['font.sans-serif'] = ['SimHei']  # Specify the default font
plt.rcParams['axes.unicode_minus'] = False  # Solve the problem of the minus sign '-' displaying as a square
