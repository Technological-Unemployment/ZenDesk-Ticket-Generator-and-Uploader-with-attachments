import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages

def create_t_chart(df, variable, save_path):
    """
    Creates and saves a T chart as a PDF.

    Args:
        df (pd.DataFrame): DataFrame containing the data to plot.
        variable (str): The column name to plot.
        save_path (str): The path where the PDF will be saved.
    """
    fig, ax = plt.subplots(figsize=(13, 5))
    
    # Define upper limits for the Y-axis based on variable type
    a = np.nanmax(df.get('variableB', 0))
    b = np.nanmax(df.get('variableC', 0))
    c = max(a, b) + 2.0
    d = np.nanmax(df.get('variableA', 0)) + 2.0

    if variable == 'variableA':
        plt.ylim(0, d)
    elif variable in ['variableB', 'variableC']:
        plt.ylim(0, c)
    elif variable == 'zs':
        plt.ylim(-1.0, 1)

    ax.plot(df['newdate'], df[variable], "o-")
    plt.grid(axis="y")
    plt.xticks(df['newdate'], rotation=0)
    plt.gca().margins(x=0)
    plt.gcf().canvas.draw()

    # Set layout for better fit of x-tick labels
    tl = plt.gca().get_xticklabels()
    maxsize = max([t.get_window_extent().width for t in tl])
    m = 0.5  # inch margin
    s = maxsize / plt.gcf().dpi * (len(df.index)) + 2 * m
    margin = m / plt.gcf().get_size_inches()[0]
    plt.gcf().subplots_adjust(left=margin, right=1.0 - margin)
    plt.gcf().set_size_inches(s, plt.gcf().get_size_inches()[1])

    # Add lines for mean, median, USL, LSL
    median = df[variable].median()
    mean = df[variable].mean()
    USL = df.get('USL', np.nan)
    LSL = df.get('LSL', np.nan)

    if variable in ['variableB', 'variableC', 'variableA']:
        plt.axhline(y=median, linestyle='-.', color='orange', label='Median')
    else:
        plt.axhline(y=mean, linestyle='--', color='g', label='Mean')

    plt.axhline(y=USL, color="k", label="USL")

    if not pd.isna(LSL):
        plt.axhline(y=LSL, color="k", label="LSL")

    plt.suptitle(f"{df.iloc[0, 0]} - {variable} Chart", fontsize=16)
    plt.ylabel(f"Average {variable} per Event", fontsize=15)
    plt.legend(loc="best", facecolor="white", frameon=True)
    
    # Save the figure as a PDF
    plt.savefig(save_path)
    plt.close()

def create_density_plot(df2, save_path):
    """
    Creates and saves a density plot as a PDF.

    Args:
        df2 (pd.DataFrame): DataFrame containing the data to plot.
        save_path (str): The path where the PDF will be saved.
    """
    with PdfPages(save_path) as pdf:
        sns.set_style("whitegrid")
        rect = patches.Rectangle(
            (-1, 1.5), 2, 2, linewidth=1, edgecolor="k", facecolor="none"
        )
        zone = sns.jointplot(
            x=df2["side"],
            y=df2["height"],
            kind="kde",
            color="red",
            shade_lowest=False,
        )
        zone.ax_joint.add_patch(rect)
        zone.ax_joint.set_xlim(-2, 2)
        zone.ax_joint.set_ylim(1, 4)
        plt.title(f"{df2.iloc[0, 0]} - Density Plot Title - 2020", fontsize=10, loc="right")
        pdf.savefig()
        plt.close()
