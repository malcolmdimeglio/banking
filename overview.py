#! /usr/bin/env python3

import sys, os
import pandas as pd
import matplotlib.pyplot as plt
import re
import math
from datetime import date
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import numpy

# To get rid of pandas' matplotlib "FutureWarning"
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


csv_folder = os.path.dirname(os.path.abspath(__file__)) + "/statements"
output_pdf = os.path.dirname(os.path.abspath(__file__)) + "/statements/overview.pdf"
header = ["date","place","amount"]

Groceries = ["iga", "save on foods", "nesters", "t&t", "kiki", "yig", "persia foods", "whole foods",
             "organic acres market", "danial market", "choices", "safeway"]

Transport = ["car2go", "evo car share", "avis", "rentals", "petrocan", "husky", "[^a-z]esso",
             "super save", "cab[^a-rt-z]",  "compass", "taxi", "shell", "poparide", "uber", "lyft", "amtrack", "boltbus"]

Restaurant = ["doordash", "skipthedishes", "restau", "a&w", "cuisine",
              "moxie's", "burger", "la belle patate", "pho", "pizza", "bestie",
              "kitchen", "thai", "el camino's", "grill", "ice cream", "japanese",
              "kaori izakaya", "taco", "mexican", "zipang provisions", "mr. steak", "poke", "sushi", "earls",
              "mcdonald's", "diner", "subway sandwiches", "falafel", "donair", "fish", "pizz", "poutine",
              "white spot", "vij's", "the capital", "cactus club", "cantina", "fork", "denny's", "mumbai local",
              "freshii", "captain's boil", "korean", "salade de fruits", "a & w", "ebisu", "mcdonald's", "cuchillo",
              "joe fortes", "the templeton", "freshii", "catering", "mary's", "meat & bread", "church's chicken",
              "rosemary rocksalt", "food", "deli", "red robin", "food", "snack", "banter room", "tap house"]

Coffee = ["cafe", "coffee", "tim hortons", "starbucks", "bean", "birds & the beets", "the mighty oak",
          "le marche st george", "caffe", "coco et olive", "buro", "blenz", "green horn", "bakery", "revolver",
          "cardero bottega", "the anchor eatery", "savary island pie", "pie", "red umbrella"]

Bar = ["brew", "beer", "pub[^a-z]", "steamworks", "distillery", "bar[^a-z]", "narrow lounge", "rumpus room",
       "five point", "score on davie", "tap & barrel", "the cambie", "colony", "alibi room", "local ",
       "per se social corner", "grapes & soda", "portland craft", "the new oxford", "keefer", "liquor", "wine", "tapshack"]

GROCERIES = 'groceries'
TRANSPORT = 'transport'
RESTAURANT = 'restaurant'
COFFEE = 'coffee'
BAR = 'bar'
MISC = 'misc'

colours = ['#5DADE2',  # blue
           '#F5B041',  # orange
           '#58D68D',  # green
           '#EC7063',  # red
           '#BB8FCE',  # purple
           '#808B96',  # grey
           '#F7DC6F']  # yellow


# @brief      Determines if row['place'] is in the given category.
#
# @param      my_row   Single row [date,place,amount] of a dataframe
# @param      my_list  Category list
#
# @return     True if row in category, False otherwise.
#
def is_row_in_category(my_row, my_list):
    for el in my_list:
        if re.search(el, my_row['place']):
            return True
    return False


# @brief      Populate a given dataframe with a given row
#
# @param      _df   Dataframe to populate
# @param      row   Row to be added to the provided dataframe
#
# @return     The updated dataframe
#
def populate(_df, row):
    _df = _df.append({'date': row['date'],
                      'place': row['place'],
                      'amount': row['amount']},
                     ignore_index=True)
    return _df


#
# @brief      Parse all spending and populate smaller dataframes by categories
#
# @param      my_dataframe  Unparsed dataframe with all uncategorized expenses
#
# @return     A dictionary of dataframe. [key] = category name; [value] = dataframe with the all categorie's related expenses
#
def organise_data_by_category(my_dataframe):
    print("Organise spendings into categories")

    # it is 3 times faster to create a dataframe from a full dictionary rather than appending rows after rows to an already existing dataframe
    dic_groc, dic_trans, dic_rest, dic_coffee, \
        dic_bar, dic_misc = {}, {}, {}, {}, {}, {}
    g, t, r, c, b, m = [0]*6  # indexes

    # Let's go over each rows of the unsorted dataframe and populate the category's dictionary.
    for index, row in my_dataframe.iterrows():
        if is_row_in_category(row, Groceries):
            dic_groc[g] = row
            g = g+1
            continue

        if is_row_in_category(row, Transport):
            dic_trans[t] = row
            t = t+1
            continue

        if is_row_in_category(row, Restaurant):
            dic_rest[r] = row
            r = r+1
            continue

        if is_row_in_category(row, Coffee):
            dic_coffee[c] = row
            c = c+1
            continue

        if is_row_in_category(row, Bar):
            dic_bar[b] = row
            b = b+1
            continue

        # If none of the above then let's put it in misc spending
        dic_misc[m] = row
        m = m+1

    df_groc = pd.DataFrame.from_dict(dic_groc, orient='index', columns=['date', 'place', 'amount'])
    df_trans = pd.DataFrame.from_dict(dic_trans, orient='index', columns=['date', 'place', 'amount'])
    df_rest = pd.DataFrame.from_dict(dic_rest, orient='index', columns=['date', 'place', 'amount'])
    df_coffee = pd.DataFrame.from_dict(dic_coffee, orient='index', columns=['date', 'place', 'amount'])
    df_bar = pd.DataFrame.from_dict(dic_bar, orient='index', columns=['date', 'place', 'amount'])
    df_misc = pd.DataFrame.from_dict(dic_misc, orient='index', columns=['date', 'place', 'amount'])

    all_df = {
        GROCERIES: df_groc,
        TRANSPORT: df_trans,
        RESTAURANT: df_rest,
        COFFEE: df_coffee,
        BAR: df_bar,
        MISC: df_misc
    }

    return all_df


# @brief      Sumarize for each month the total spending for a given category
#
# @param      _df       An organized by category dataframe
# @param      category  The category name you want to extract the information of
#
# @return     A dataframe with only 1 category's information and the sum of all the spendings for that category, listed by month
#
def extract_monthly_spending(_df, category):
    print("Extract monthly spendings for {}".format(category))
    df_temp = pd.DataFrame(columns=['date', 'amount'])

    if _df[category].empty:
        df_temp.name = category
        return df_temp

    # let's only do the math between the first and last spending day in the csv file to avoid
    # blank values at the begining and the end of the charts
    #
    # max_year = all_spending_df['date'].max().year
    max_year = date.today().year
    min_year = all_spending_df['date'].min().year
    min_month = all_spending_df['date'].min().month
    # max_month = all_spending_df['date'].max().month
    max_month = date.today().month

    for year in range(min_year, max_year + 1):
        if year == min_year:
            start_month = min_month
        else:
            start_month = 1

        if year == max_year:
            end_month = max_month
        else:
            end_month = 12

        # sum all spending from a whole month, each month of the year
        for month in range(start_month, end_month + 1):
            df_temp = df_temp.append({"date": "{}-{}".format(month, year),
                                     "amount": _df[category].loc[(_df[category].date.dt.month == month) &
                                                                 (_df[category].date.dt.year == year), 'amount'].sum()},
                                     ignore_index=True)
    df_temp.name = category
    df_temp['date'] = pd.to_datetime(df_temp['date'])
    df_temp.set_index('date', inplace=True)

    return df_temp

#
# @brief      Attach a text label above each ploted bar.
#
# @param      rects   The rectangles (each ploted bar)
# @param      ax      Axis
# @param      height  The height (monthy $ value)
#
def autolabel(rects, ax, height):
    for index, rect in enumerate(rects):
        ax.annotate('{}'.format(int(height[index])),
                    xy=(rect.get_x() + rect.get_width() / 2, height[index]),
                    xytext=(0, 1),  # 1 points vertical offset
                    textcoords="offset points",
                    ha='center',
                    va='bottom')


#
# @brief      Calculates the average.
#
# @param      _df            The dataframe to extract the spending mean value of
# @param      period_months  The period months from today's date to calculate the average of
# @param      absolute       Boolean. If False the average computation will no consider the min value and max value for calculation.
#
# @return     The average spending over the las 'period_months'. Also return min and max value over the same period of time
#
def compute_average(_df, period_months=0, absolute=False):
    today = date.today()

    # Allows to compute the average over the last period_months time
    if period_months > 0:
        from_date = today - pd.DateOffset(months=int(period_months))
        from_date = _df.index.min() if from_date < _df.index.min() else from_date  # keep lower boundary at first date recorded

        _df = _df.drop(_df[_df.index < pd.to_datetime(from_date)].index)

    # To calculate the average, let's get rid of the extremums (only if we don't want an absolute average), the current month and all 0$ spending months
    if not absolute:
        _df = _df.drop(_df[_df.amount == _df.amount.max()].index)
        _df = _df.drop(_df[_df.amount == _df.amount.min()].index)
    _df = _df.drop(_df[(_df.index.month == today.month) & (_df.index.year == today.year)].index)
    _df = _df.drop(_df[_df.amount == 0].index)

    # Handles the cases where after dropping all the rows we end up with an empty dataframe
    if numpy.isnan(_df.min().amount):
        _min = 0
    else:
        _min = int(_df.min().amount)

    if numpy.isnan(_df.max().amount):
        _max = 0
    else:
        _max = int(_df.max().amount)

    if numpy.isnan(_df.mean().amount):
        _mean = 0
    else:
        _mean = int(_df.mean().amount)

    return _min, _max, _mean


#
# @brief      Will plot a bar chart for each category. X axis will be scaled by month.
#
# @param      _df_list  List that contains each categorie's dataframe spending per month
#
# @return     The figure with all the charts
#
def render_monthly_bar_by_cat(_df_list):
    # 3 columns display
    col = 3
    row = len(_df_list) / 3
    if math.modf(row)[0] != 0.0:
        row += 1

    fig, ax = plt.subplots(int(row), int(col), figsize=(30, 15))
    ax = ax.flatten()

    i = 0
    for el in _df_list:
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
            _, _, avg = compute_average(el)
            _, _, avg6 = compute_average(el, period_months=6)

            if avg > 0:  # No need to plot the average if it's 0
                ax[i].axhline(y=avg,
                              color="red",
                              linewidth=0.5,
                              label='avg',
                              linestyle='--')
                ax[i].annotate('{}'.format(avg),
                               xy=(el.index[0], avg),
                               xytext=(-10, 1),  # 3 points vertical offset
                               textcoords="offset points",
                               ha='right',
                               va='bottom',
                               color='red')
            if avg6 > 0:  # No need to plot the average if it's 0
                ax[i].axhline(y=avg6,
                              color="blue",
                              linewidth=0.5,
                              label='avg 6 months',
                              linestyle='--')
                ax[i].annotate('{}'.format(avg6),
                               xy=(el.index[0], avg6),
                               xytext=(-10, 1),  # 3 points vertical offset
                               textcoords="offset points",
                               ha='right',
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

        i += 1

    # Remove unused plots
    for j in range(i, len(ax)):
        ax[j].set_axis_off()

    plt.tight_layout(w_pad=2.3, h_pad=1.3)
    return fig


#
# @brief      Will plot a stacked bar chart. Displaying the total amount of spending per month, stacking all categories together
#
# @param      _df_list  List that contains each categorie's dataframe spending per month
#
# @return     The figure with the calculated chart
#
def render_monthly_bar_stacked(_df_list):
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
                    color=colours[i],
                    label='monthly')
        ax.annotate('NO DATA',
                    xy=(date.today(), 0),
                    xytext=(0, 0),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center',
                    va='center',
                    color='red',
                    fontsize=50)

    autolabel(bar, ax, bottom_value)

    # 45 deg angle for X labels
    plt.setp(ax.get_xticklabels(),
             rotation=45,
             ha="right")

    # Add XY labels and title
    ax.title.set_weight('extra bold')
    ax.title.set_fontsize('xx-large')
    ax.title.set_text("Month by month spending")
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

    plt.tight_layout(w_pad=200, h_pad=500)
    return fig


#
# @brief      Will plot a pie chart representing the proportion of spending by category
#
# @param      _df   A dataframe contaning the average overall spending by category
#
# @return     The figure with the calculated chart
#
def render_average_pie(_df_list):
    print("Render average spending by category on pie chart")

    avg_df = pd.DataFrame(columns=['name', 'amount'])

    for el in _df_list:
        if not el.empty:  # Do not handle categories with no data
            _, _, average = compute_average(el, absolute=True)
            avg_df = avg_df.append({'name': el.name, 'amount': average}, ignore_index=True)

    fig, ax = plt.subplots(1, 1, figsize=(30, 15))
    explodes = [0.0] * len(avg_df)
    explodes[0] = 0.2  # select the 0 index to explode the piece of the pie. The value has been determined by visual tests
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


if __name__ == "__main__":
    try:
        tmp_list = []
        for file in os.listdir(csv_folder):
            if file.lower().endswith('.csv'):
                csv_file = csv_folder + '/' + file
                print(f"Read CSV file {file}...")
                # Extract csv into dataframe
                tmp_list.append(pd.read_csv(filepath_or_buffer=csv_file, sep=',', names=["date","place","amount"]))
    except FileNotFoundError:
        print('** ERROR ** File {} not found'.format(csv_file))
        sys.exit()

    all_spending_df = pd.concat(tmp_list, axis=0, ignore_index=True, sort=False)

    print("Remove incomes, standardize text and date")
    # Remove all incomes
    all_spending_df = all_spending_df[all_spending_df.amount < 0]
    if all_spending_df.empty:
        print("It seems your CSV file content is either empty or does not contain any debit on your credit history. \
        \nPlease check the content of {}".format(os.path.basename(csv_file)))
        sys.exit()

    # Change spending into positive values, lower case the 'place' column and datetime format for the 'date' column
    all_spending_df['amount'] = all_spending_df['amount'].apply(lambda x: -x)  # Maybe more efficient not to and just do that at the very end when ploting the graph?
    all_spending_df['place'] = all_spending_df["place"].apply(lambda x: x.lower())
    all_spending_df['date'] = pd.to_datetime(all_spending_df['date'])

    data = organise_data_by_category(all_spending_df)
    monthly_groceries = extract_monthly_spending(data, GROCERIES)
    monthly_transport = extract_monthly_spending(data, TRANSPORT)
    monthly_restaurant = extract_monthly_spending(data, RESTAURANT)
    monthly_coffee = extract_monthly_spending(data, COFFEE)
    monthly_bar = extract_monthly_spending(data, BAR)
    monthly_misc = extract_monthly_spending(data, MISC)

    monthly_spending = [monthly_groceries, monthly_transport, monthly_restaurant,
                        monthly_coffee, monthly_bar, monthly_misc]

    figures = []
    figures.append(render_monthly_bar_by_cat(monthly_spending))
    figures.append(render_monthly_bar_stacked(monthly_spending))
    figures.append(render_average_pie(monthly_spending))

    # TODO: Check output_pdf valid path to file
    doc = PdfPages(output_pdf)
    for figure in figures:
        figure.savefig(doc, format='pdf')
    doc.close()
    print("Output PDF document: {}".format(output_pdf))

    if len(sys.argv) > 1 and sys.argv[1].lower() == "debug":
        print("\n--- DEBUG ---")
        print("Content of full dataframe organized by categories \n")
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(data)

