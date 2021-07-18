# -*- coding: utf-8 -*-
from numbers import Number
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union
from scipy import stats
import numpy as np
import numba
import matplotlib.pyplot as plt

NumberArrayType = Union[Number, List[Number], np.ndarray]
""" Input data for computing/returning distributions. """

ScatterPlotDataType = Tuple[NumberArrayType, NumberArrayType]
""" Output data intended for scatter plotting. """


def ecdf_formal(x: NumberArrayType,
                data: np.ndarray) -> NumberArrayType:
    """ Compute the formal ECDF from `data` at `x`.

    Parameters
    ----------
    x : NumberArrayType
        Positions at which the formal ECDF is to be evaluated.
    data : np.ndarray
        One-dimensional array of data to use to generate the ECDF.

    Returns
    -------
    NumberArrayType
        Value of the ECDF at `x`.

    Raises
    ------
    RuntimeError
        Input data contains NaN's.
    """
    # If x has any nans, raise a RuntimeError
    if np.isnan(x).any():
        raise RuntimeError('Input cannot have NaNs.')

    # Convert x and data to arrays with no NaN's.
    x_arr = _convert_data(x, inf_ok=True)
    data = _convert_data(data, inf_ok=True)

    # Compute formal ECDF value
    out = _ecdf_formal(x_arr, np.sort(data))

    # Return according to the type of input.
    return out[0] if np.isscalar(x) else out


def ecdf(data: np.ndarray,
         formal: Optional[bool] = False,
         buff: Optional[Number] = 0.1,
         min_x: Optional[Number] = None,
         max_x: Optional[Number] = None) -> ScatterPlotDataType:
    """ Generate `x` and `y` values for plotting an ECDF.

    During conversion all NaN's are dropped.

    Parameters
    ----------
    data : np.ndarray
        One-dimensional array of data to be plotted as an ECDF.
    formal : Optional[bool]
        If True, generate `x` and `y` values for formal ECDF.
        Otherwise, generate `x` and `y` values for "dot" style ECDF.
        Default is `False`.
    buff : Optional[Number]
        How long the tails at y = 0 and y = 1 should extend as a
        fraction of the total range of the data. Ignored if
        `formal` is False. Default is `0.1`.
    min_x : Optional[Number]
        Minimum value of `x` to include on plot. Overrides `buff`.
        Ignored if `formal` is False. Default is `None`.
    max_x : Optional[Number]
        Maximum value of `x` to include on plot. Overrides `buff`.
        Ignored if `formal` is False. Default is `None`.

    Returns
    -------
    ScatterPlotDataType
        Tuple of `x` and `y` values for plotting.

    Raises
    ------
    RuntimeError
        If `x` range and `buff` not provided but `formal` is `True`.
    """
    if formal and buff is None and (min_x is None or max_x is None):
        msg = 'If `buff` is None, requires `min_x` and `max_x`.'
        raise RuntimeError(msg)

    if not formal:
        return _ecdf_dots(_convert_data(data))

    args = (buff, min_x, max_x)
    return _ecdf_formal_for_plotting(_convert_data(data), *args)


def compare_ecdf(df, var, categories, display_norm=True,
                 pval_ref=0.05):
    """ Compare categories through ECDF.

    df : pd.DataFrame
        Dataframe with selected column.
    var : str
        Column to compare categorical level.
    categories : List[Tuple[List[bool], str]]
        List of row selectors and labels for plotting.
    """
    arrs = []

    for q_, lab_ in categories:
        val = df.loc[q_, var].values
        x, y = ecdf(val)
        label = F'{lab_} ({val.mean():.2e} ± {2*val.std():.2e})'
        p = plt.plot(x, y, marker='.', linestyle='', label=label)

        if len(categories) == 2:
            arrs.append(x)

        if display_norm:
            c_ = p[0].get_color()
            x_ = np.linspace(x.min(), x.max(), 100)
            y = stats.norm.cdf(x_, loc=val.mean(), scale=val.std())
            plt.plot(x_, y, c_, ls='-.', label='_none_')

    if len(categories) == 2:
        _, pval = stats.ttest_ind(*arrs)
        res = 'identical' if pval > pval_ref else 'distinct'
        plt.title(F'p-value {pval:.4f} ({pval_ref}): {res} means')

    plt.xlabel(var)
    plt.ylabel('Probability')
    plt.legend(loc='best')
    plt.grid(linestyle=':')
    plt.tight_layout()


def _convert_data(data: NumberArrayType,
                  inf_ok: Optional[bool] = False,
                  min_len: Optional[int] = 1) -> np.ndarray:
    """ Convert 1D data set into NumPy array of floats.

    During conversion all NaN's are dropped.

    Parameters
    ----------
    data : NumberArrayType
        Input data, to be converted.
    inf_ok : Optional[bool]
        If True, np.inf values are allowed in the arrays.
        Default is `False`.
    min_len : Optional[int]
        Minimum length of array. Default is `1`.

    Returns
    -------
    np.ndarray
        One-dimensional NumPy array from `data`, dtype float.

    Raises
    ------
    RuntimeError
        Input data is not scalar (0D) or one-dimensional (1D).
        Input data contains infinite numbers and `inf_of==False`.
        Input data length is lower than `min_len`.
    """
    # Convert data to NumPy array according to type.
    newdata = [data] if np.isscalar(data) else data
    newdata = np.array(newdata, dtype=np.float)

    # Make sure it is 1D after transforming to array.
    if len(newdata.shape) != 1:
        raise RuntimeError('Input must be a 1D array.')

    # Drop NaNs from data.
    newdata = newdata[~np.isnan(newdata)]

    # Check for infinite entries
    if not inf_ok and np.isinf(newdata).any():
        raise RuntimeError('All entries must be finite.')

    # Check to minimal length
    if len(newdata) < min_len:
        raise RuntimeError(F'Must have at least {min_len} non-NaN.')

    return newdata


@numba.jit(nopython=True)
def _ecdf_formal(x: NumberArrayType,
                 data: np.ndarray) -> NumberArrayType:
    """ Compute the formal ECDF from `data` at `x`.

    Parameters
    ----------
    x : NumberArrayType
        Positions at which the formal ECDF is to be evaluated.
    data : np.ndarray
        Sorted 1D array of data to use to generate the ECDF.

    Returns
    -------
    NumberArrayType
        Value of the ECDF at `x`.
    """
    output = np.empty_like(x)

    for i, x_val in enumerate(x):
        j = 0
        while j < len(data) and x_val >= data[j]:
            j += 1

        output[i] = j

    return output / len(data)


@numba.jit(nopython=True)
def _ecdf_dots(data: np.ndarray) -> ScatterPlotDataType:
    """ Generate `x` and `y` values for plotting an ECDF.

    During conversion all NaN's are dropped.

    Parameters
    ----------
    data : np.ndarray
        One-dimensional array of data to be plotted as an ECDF.

    Returns
    -------
    ScatterPlotDataType
        Tuple of `x` and `y` values for plotting.
    """
    return np.sort(data), np.arange(1, len(data) + 1) / len(data)


@numba.jit(nopython=True)
def _ecdf_formal_for_plotting(data: np.ndarray, buff: Number,
                              min_x: Number, max_x: Number
                              ) -> ScatterPlotDataType:
    """ Generate `x` and `y` values for plotting an ECDF.

    During conversion all NaN's are dropped.

    Parameters
    ----------
    data : np.ndarray
        One-dimensional array of data to be plotted as an ECDF.
    buff : Number
        How long the tails at y = 0 and y = 1 should extend as a
        fraction of the total range of the data. Ignored if
        `formal` is False.
    min_x : Number
        Minimum value of `x` to include on plot. Overrides `buff`.
        Ignored if `formal` is False.
    max_x : Number
        Maximum value of `x` to include on plot. Overrides `buff`.
        Ignored if `formal` is False.

    Returns
    -------
    ScatterPlotDataType
        Tuple of `x` and `y` values for plotting.
    """
    # Get x and y values for data points.
    x, y = _ecdf_dots(data)

    # Set defaults for min and max tails.
    if min_x is None:
        min_x = x[0] - (x[-1] - x[0]) * buff
    if max_x is None:
        max_x = x[-1] + (x[-1] - x[0]) * buff

    # Set up output arrays.
    x_formal = np.empty(2 * (len(x) + 1))
    y_formal = np.empty(2 * (len(x) + 1))

    # y-values for steps.
    y_formal[:2] = 0
    y_formal[2::2] = y
    y_formal[3::2] = y

    # x-values for steps.
    x_formal[0] = min_x
    x_formal[1] = x[0]
    x_formal[2::2] = x
    x_formal[3:-1:2] = x[1:]
    x_formal[-1] = max_x

    return x_formal, y_formal
