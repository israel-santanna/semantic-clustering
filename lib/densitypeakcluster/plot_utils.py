#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# The MIT License (MIT)

# Copyright (c) 2014 Jason

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy as np
import matplotlib.pyplot as plt


def plot_scatter_diagram(which_fig, x, y, x_label='x', y_label='y', title='title', style_list=None):
    '''
    Plot scatter diagram

    Args:
            which_fig  : which sub plot
            x          : x array
            y          : y array
            x_label    : label of x pixel
            y_label    : label of y pixel
            title      : title of the plot
    '''
    # styles = ['k.', 'g.', 'r.', 'c.', 'm.', 'y.', 'b.']
    assert len(x) == len(y)
    if style_list is not None:
        assert len(x) == len(style_list) 
        #and len(styles) >= len(set(style_list))
    plt.figure(which_fig)
    plt.clf()
    if style_list is None:
        # plt.plot(x, y, styles[0])
        plt.plot(x, y, 'k.')
    else:
        clses = set(style_list)
        styles = [plt.cm.Spectral(each) 
                  for each in np.linspace(0, 1, len(clses))]
        xs, ys = {}, {}
        for i in range(len(x)):
            try:
                xs[style_list[i]].append(x[i])
                ys[style_list[i]].append(y[i])
            except KeyError:
                xs[style_list[i]] = [x[i]]
                ys[style_list[i]] = [y[i]]
        for idx, cls in enumerate(clses):
            if cls == -1:
                style = [0, 0, 0, 1]
            else:
                style = styles[idx]
            plt.plot(xs[cls], ys[cls], 'o', markerfacecolor=tuple(style),
             markeredgecolor='k')
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.ylim(bottom=0)
    plt.show()


if __name__ == '__main__':
    x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 7, 7])
    y = np.array([2, 3, 4, 5, 6, 2, 4, 8, 5, 6])
    cls = np.array([1, 4, 2, 3, 5, -1, -1, 6, 6, 6])
    plot_scatter_diagram(0, x, y, style_list=cls)
