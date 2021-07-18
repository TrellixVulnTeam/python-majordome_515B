# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def plot_correlation(df: pd.DataFrame):
    """ Plot correlation matrix of dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to compute and displayu correlation matrix.

    Returns
    -------
    Figure
        A matplotlib figure to write to file or display.
    """
    # Compute correlation matrix.
    corr = df.corr()

    # Set seaborn style.
    sns.set(style='white')

    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(corr, dtype=np.bool))

    # Set up the matplotlib figure
    fig, ax = plt.subplots(figsize=(11, 9))

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr, mask=mask, cmap='seismic', center=0.0,
                square=True, linewidths=0.5)

    fig.tight_layout()
    return fig
