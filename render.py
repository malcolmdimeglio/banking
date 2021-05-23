#! /usr/bin/env python3

import math
import numpy
from pandas.tseries.offsets import MonthEnd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import date

colours = ['#5DADE2',  # blue
           '#F5B041',  # orange
           '#58D68D',  # green
           '#EC7063',  # red
           '#BB8FCE',  # purple
           '#808B96',  # grey
           '#F7DC6F']  # yellow


def autolabel(rects, ax, height):
    """Attach a text label above each ploted bar

    Args:
        rects (matplotlib.container.BarContainer): The rectangles (each ploted bar)
        ax (matplotlib.axes._subplots.AxesSubplot): Axis
        height (pandas.core.series.Series): The height (monthy $ value)
    """

    for index, rect in enumerate(rects):
        ax.annotate('{}'.format(int(height[index])),
                    xy=(rect.get_x() + rect.get_width() / 2, height[index]),
                    xytext=(0, 1),  # 1 points vertical offset
                    textcoords="offset points",
                    ha='center',
                    va='bottom')


def compute_average(_df, forMonths=0, endDay=pd.datetime.now().date(), absolute=False):
    """Calculates the average value in the 'amount' column of a given dataframe

    Args:
        _df (pandas.core.frame.DataFrame): The dataframe to extract the spending mean value of
        forMonths (int, optional): The period months from today's date to calculate the average of. Defaults to 0.
        endDay (pandas._libs.tslibs.timestamps.Timestamp, optional): Boolean. If False the average computation will no consider the min value and max value for calculation. Defaults to pd.datetime.now().date().
        absolute (bool, optional): Datetime type. Calculate average until this day and for the past {forMonths}. Defaults to False.

    Returns:
        int: The average spending over the last 'forMonths'
    """

    # Allows to compute the average over the last forMonths time
    if forMonths > 0:
        fromDay = endDay - pd.DateOffset(months=int(forMonths))
        fromDay = _df.index.min() if fromDay < _df.index.min() else fromDay  # keep lower boundary at first date recorded
    else:
        fromDay = _df.index.min()

    fromDay = fromDay.date()  # remove hour, minute, second

    # drop everything not in the range [from;until]
    _df = _df.drop(_df[_df.index < pd.to_datetime(fromDay)].index)
    _df = _df.drop(_df[_df.index > pd.to_datetime(endDay)].index)

    # To calculate the average, let's get rid of the extremums (only if we don't want an absolute average), the current month and all 0$ spending months
    if not absolute:
        _df = _df.drop(_df[_df.amount == _df.amount.max()].index)
        _df = _df.drop(_df[_df.amount == _df.amount.min()].index)
        _df = _df.drop(_df[_df.amount == 0].index)

    # get rid of any data of the current month as it is not complete.
    _df = _df.drop(_df[(_df.index.month == date.today().month) & (_df.index.year == date.today().year)].index)

    # Handles the cases where after dropping all the rows we end up with an empty dataframe
    _mean = 0 if numpy.isnan(_df.mean().amount) else int(_df.mean().amount)

    return _mean


def monthly_bar_by_cat(_df_list, useAbsoluteAvg=False):
    """Will plot a bar chart for each category. X axis will be scaled by month

    Args:
        _df_list (list): List that contains each categorie's dataframe spending per month
        useAbsoluteAvg (bool, optional): If False the average computation will no consider the min value and max value for calculation. Defaults to False.

    Returns:
        matplotlib.figure.Figure: The figure with all the charts
    """

    # 3 columns display
    col = 3
    row = len(_df_list) / 3
    if math.modf(row)[0] != 0.0:
        row += 1

    fig, ax = plt.subplots(int(row), int(col), figsize=(30, 15))
    ax = ax.flatten()

    for i, el in enumerate(_df_list):
        print("Render monthy spending on bar graph for {}".format(el.name))

        if el.empty:
            bar = ax[i].bar(date.today(),
                            0,
                            color=colours[i],
                            label='monthly')
            ax[i].annotate('NO DATA',
                           xy=(date.today(), 0),
                           xytext=(0, 0),  # 3 points vertical offset
                           textcoords="offset points",
                           ha='center',
                           va='center',
                           color='red',
                           fontsize=50)
        else:
            bar = ax[i].bar(el.index.values,
                            el['amount'],
                            color=colours[i],
                            label='monthly',
                            width=150 * (1 / el.shape[0]))

            # Plot the average monthly spending on the corresponding graph
            # Let's plot past averages over multiple 6 months periods as well as an all time average

            # Start calculating from last month's last day
            _endPeriod = date.today() - pd.DateOffset(months=1)
            _endPeriod += MonthEnd(0)

            _6monthsAvgDates = []
            _6monthsAvgValues = []

            compute = True
            while(compute):
                avgOver6mth = compute_average(el, endDay=_endPeriod, forMonths=6, absolute=True)
                _6monthsAvgValues.append(avgOver6mth)
                _6monthsAvgDates.append(_endPeriod)

                _endPeriod -= pd.DateOffset(months=6)  # New end period moved back 6months
                if _endPeriod <= el.index.min():  # We've reached the end of the dataframe
                    _endPeriod = el.index.min()
                    compute = False

                _6monthsAvgDates.append(_endPeriod)
                _6monthsAvgValues.append(avgOver6mth)

            ax[i].plot(_6monthsAvgDates, _6monthsAvgValues, '-o',
                       color='red',
                       label="Avg over 6 months period")
            for j, val in enumerate(zip(_6monthsAvgDates, _6monthsAvgValues)):
                # _6monthsAvgDates is ordered from recent to old so the plot "starts" from the right
                # We don't need to annotate twice the same value. let's skip one.
                if j % 2 > 0:
                    ax[i].annotate('{}'.format(val[1]),
                                   xy=val,
                                   xytext=(-5, 1),  # 3 points vertical offset
                                   textcoords="offset points",
                                   ha='right',
                                   va='bottom',
                                   color='red')

            avg = compute_average(el, absolute=useAbsoluteAvg)
            if avg > 0:  # No need to plot the average if it's 0
                ax[i].axhline(y=avg,
                              color="blue",
                              linewidth=0.5,
                              label='all time avg',
                              linestyle='--')
                ax[i].annotate('{}'.format(avg),
                               xy=(el.index[0] - pd.DateOffset(months=1), avg),
                               ha='left',
                               va='bottom',
                               color='blue')

            autolabel(bar, ax[i], el['amount'])

            # 45 deg angle for X labels
        plt.setp(ax[i].get_xticklabels(),
                 rotation=45,
                 ha="right")

        # Add XY labels and title
        ax[i].title.set_weight('extra bold')
        ax[i].title.set_fontsize('xx-large')
        ax[i].title.set_text("{}".format(el.name).title())
        ax[i].set_ylabel('Spending ($)', fontsize='xx-large')
        ax[i].set_xlabel('Date', fontsize='xx-large')

        # Set the locator
        locator = mdates.MonthLocator()  # every month
        # Specify the format - %b gives us Jan, Feb...
        fmt = mdates.DateFormatter('%b %Y')

        ax[i].xaxis.set_major_locator(locator)
        # Specify formatter
        ax[i].xaxis.set_major_formatter(fmt)
        ax[i].legend()

    # Remove unused plots
    for j in range(i + 1, len(ax)):
        ax[j].set_axis_off()

    plt.tight_layout(w_pad=2.3, h_pad=1.3)

    return fig


def monthly_bar_stacked(_df_list, useAbsoluteAvg=False, title="Month by month spending"):
    """[summary]

    Args:
        _df_list (list): List that contains each categorie's dataframe spending per month
        useAbsoluteAvg (bool, optional): If False the average computation will no consider the min value and max value for calculation. Defaults to False.
        title (str, optional): Give your graph a tittle. Defaults to "Month by month spending".

    Returns:
        matplotlib.figure.Figure: The figure with the calculated chart
    """

    print("Render monthy spending on stack graph for all categories")
    fig, ax = plt.subplots(1, 1, figsize=(30, 15))

    bottom_value = 0
    empty_chart = True
    for index, el in enumerate(_df_list):
        if not el.empty:
            empty_chart = False
            bar = ax.bar(el.index.values,
                         el['amount'],
                         color=colours[index],
                         label=el.name,
                         bottom=bottom_value,
                         width=150 * (1 / el.shape[0]))
            bottom_value += _df_list[index]['amount']

    if empty_chart:
        bar = ax.bar(date.today(),
                     0,
                     color=colours[index],
                     label='monthly')
        ax.annotate('NO DATA',
                    xy=(date.today(), 0),
                    xytext=(0, 0),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center',
                    va='center',
                    color='red',
                    fontsize=50)
    else:
        # Create a dataframe holding the total spendings per month, regardless of their category
        tot_spending = pd.DataFrame(columns=['date', 'amount'])
        tot_spending.set_index('date', inplace=True)
        for _df in _df_list:
            tot_spending = tot_spending.add(_df, fill_value=0)

        # Plot the average monthly spending on the corresponding graph
        avg = compute_average(tot_spending, absolute=useAbsoluteAvg)

        if avg > 0:  # No need to plot the average if it's 0
            ax.axhline(y=avg,
                       color="blue",
                       linewidth=0.5,
                       label='all time avg',
                       linestyle='--')
            ax.annotate('{}'.format(avg),
                        xy=(tot_spending.index[0] - pd.DateOffset(months=1) + pd.DateOffset(days=2), avg),
                        ha='right',
                        va='bottom',
                        color='blue')

        # Start calculating from last month's last day
        _endPeriod = date.today() - pd.DateOffset(months=1)
        _endPeriod += MonthEnd(0)

        _6monthsAvgDates = []
        _6monthsAvgValues = []

        compute = True
        while(compute):
            avgOver6mth = compute_average(tot_spending, endDay=_endPeriod, forMonths=6, absolute=True)
            _6monthsAvgValues.append(avgOver6mth)
            _6monthsAvgDates.append(_endPeriod)

            _endPeriod -= pd.DateOffset(months=6)  # New end period moved back 6months
            if _endPeriod <= tot_spending.index.min():  # We've reached the end of the dataframe
                _endPeriod = tot_spending.index.min()
                compute = False

            _6monthsAvgDates.append(_endPeriod)
            _6monthsAvgValues.append(avgOver6mth)

        ax.plot(_6monthsAvgDates, _6monthsAvgValues, '-o',
                color='red',
                label="Avg over 6 months period")

        for j, val in enumerate(zip(_6monthsAvgDates, _6monthsAvgValues)):
            # _6monthsAvgDates is ordered from recent to old so the plot "starts" from the right
            # We don't need to annotate twice the same value. let's skip one.
            if j % 2 > 0:
                ax.annotate('{}'.format(val[1]),
                            xy=val,
                            xytext=(-5, 1),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='right',
                            va='bottom',
                            color='red')

    autolabel(bar, ax, tot_spending['amount'])

    # 45 deg angle for X labels
    plt.setp(ax.get_xticklabels(),
             rotation=45,
             ha="right")

    # Add XY labels and title
    ax.title.set_weight('extra bold')
    ax.title.set_fontsize('xx-large')
    ax.title.set_text(title)
    ax.set_ylabel('Spending ($)', fontsize='xx-large')
    ax.set_xlabel('Date', fontsize='xx-large')

    # Set the locator
    locator = mdates.MonthLocator()  # every month
    # Specify the format - %b gives us Jan, Feb...
    fmt = mdates.DateFormatter('%b %Y')

    ax.xaxis.set_major_locator(locator)
    # Specify formatter
    ax.xaxis.set_major_formatter(fmt)
    ax.legend()

    # plt.tight_layout(w_pad=200, h_pad=500)
    return fig


def average_pie(_df_list):
    """Will plot a pie chart representing the proportion of spending by category

    Args:
        _df_list (list): A list of dataframe contaning the average overall spending by category

    Returns:
        matplotlib.figure.Figure: The figure with the calculated chart
    """

    print("Render average spending by category on pie chart")

    avg_df = pd.DataFrame(columns=['name', 'amount'])

    for el in _df_list:
        if not el.empty:  # Do not handle categories with no data
            average = compute_average(el, absolute=True)
            avg_df = avg_df.append({'name': el.name, 'amount': average}, ignore_index=True)

    fig, ax = plt.subplots(1, 1, figsize=(30, 15))
    explodes = [0.0] * len(avg_df)
    explodes[1] = 0.2  # select the 1 index to explode the piece of the pie. The value has been determined by visual tests
    _, _, autotexts = ax.pie(avg_df['amount'], labels=avg_df['name'],
                             explode=explodes,
                             autopct='%1.1f%%',
                             shadow=False,
                             frame=False,
                             startangle=90,
                             colors=colours,
                             textprops={'fontsize': 'xx-large'},
                             wedgeprops={'linewidth': 1, 'edgecolor': "black"})

    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.setp(autotexts, size=15, weight="bold")
    ax.set_title("Proportion in spending")
    ax.title.set_weight('extra bold')
    ax.title.set_fontsize('xx-large')

    return fig
