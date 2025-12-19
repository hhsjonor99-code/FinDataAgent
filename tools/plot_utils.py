import os
import matplotlib.pyplot as plt

def plot_line_chart(df, x_col, y_col, title, save_path):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    x = df[x_col]
    y = df[y_col]
    plt.figure(figsize=(10, 5))
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
