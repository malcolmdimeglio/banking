#! /usr/bin/env python3

import sys
import pandas as pd
import matplotlib.pyplot as plt
import re
import math
from datetime import date
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages

# To get rid of pandas' matplotlib "FutureWarning"
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


csv_file = "/Users/Malcolm/Desktop/pcbanking.csv"
output_pdf = "/Users/Malcolm/Desktop/mytest.pdf"
header = "date,place,amount"

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

figures = []

# prepend header to csv if needed
with open(csv_file, 'r') as file:
    data = file.readline()  # read the first line
    if re.search(header, data):  # if header is present then do not modify the csv file
        do_modify = False
    else:
        do_modify = True

with open(csv_file, 'r') as file:
    data = file.read()

if do_modify:  # add header if needed
    with open(csv_file, 'w') as file:
        file.write(header + '\n' + data)

print("Read CSV file...")
# Extract csv into dataframe
all_spending_df = pd.read_csv(filepath_or_buffer=csv_file, sep=',')

print("Remove incomes, standardize text and date")
# Remove all incomes
all_spending_df = all_spending_df[all_spending_df.amount < 0]

# Change spending into positive values, lower case the 'place' column and datetime format for the 'date' column
all_spending_df['amount'] = all_spending_df['amount'].apply(lambda x: -x)
all_spending_df['place'] = all_spending_df["place"].apply(lambda x: x.lower())
all_spending_df['date'] = pd.to_datetime(all_spending_df['date'])


# Check if a given row is part of the given category
def is_row_in_category(my_row, my_list):
    for el in my_list:
        if re.search(el, my_row['place']):
            return True
    return False


# Populate a given dataframe with a given row
def populate(_df, row):
    _df = _df.append({'date': row['date'],
                      'place': row['place'],
                      'amount': row['amount']},
                     ignore_index=True)
    return _df


# Parse all spending and populate smaller dataframes by categories
def organise_data_by_category(my_dataframe):
    print("Organise spendings into categories")

    # it is 3 times faster to create a dataframe from a full dictionary rather than appending rows after rows to an already existing dataframe
    dic_groc, dic_trans, dic_rest, dic_coffee, \
        dic_bar, dic_misc = {}, {}, {}, {}, {}, {}
    g, t, r, c, b, m = [0]*6  # indexes

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


# Create a small dataframe where each month is associated with a total of spending
def extract_monthly_spending(_df, spending):
    print("Extract monthly spendings for {}".format(spending))
    df_temp = pd.DataFrame(columns=['date', 'amount'])

    max_year = all_spending_df['date'].max().year
    min_year = all_spending_df['date'].min().year
    min_month = all_spending_df['date'].min().month
    max_month = all_spending_df['date'].max().month

    # let's only do the math between the first and last spending day in the csv file.
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
                                     "amount": _df[spending].loc[(_df[spending].date.dt.month == month) &
                                                                 (_df[spending].date.dt.year == year), 'amount'].sum()},
                                     ignore_index=True)

    df_temp['date'] = pd.to_datetime(df_temp['date'])
    df_temp.set_index('date', inplace=True)
    df_temp.name = spending

    return df_temp


def autolabel(rects, ax, height):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for index, rect in enumerate(rects):
        ax.annotate('{}'.format(int(height[index])),
                    xy=(rect.get_x() + rect.get_width() / 2, height[index]),
                    xytext=(0, 1),  # 1 points vertical offset
                    textcoords="offset points",
                    ha='center',
                    va='bottom')


def compute_average(_df, period_months=0):
    today = date.today()

    # Allows to compute the average over the last period_months time
    if period_months > 0:
      from_date = today - pd.DateOffset(months=period_months)
      _df = _df.drop(_df[_df.index < pd.to_datetime(from_date)].index)

    # To calculate the average, let's get rid of the extremums, the current month and all 0$ spending months
    _df = _df.drop(_df[_df.amount == _df.amount.max()].index)
    _df = _df.drop(_df[_df.amount == _df.amount.min()].index)
    _df = _df.drop(_df[(_df.index.month == today.month) & (_df.index.year == today.year)].index)
    _df = _df.drop(_df[_df.amount == 0].index)

    return _df.min(), _df.max(), _df.mean()


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
        bar = ax[i].bar(el.index.values,
                        el['amount'],
                        color=colours[i],
                        label='monthly',
                        width=150 * (1 / el.shape[0]))

        # Plot the average monthly spending on the corresponding graph
        _, _, avg = compute_average(el)
        _, _, avg6 = compute_average(el, period_months=6)
        ax[i].axhline(y=int(avg.amount),
                      color="red",
                      linewidth=0.5,
                      label='avg',
                      linestyle='--')
        ax[i].annotate('{}'.format(int(avg.amount)),
                       xy=(monthly_coffee.index[0], int(avg.amount)),
                       xytext=(-10, 1),  # 3 points vertical offset
                       textcoords="offset points",
                       ha='right',
                       va='bottom',
                       color='red')

        ax[i].axhline(y=int(avg6.amount),
                      color="blue",
                      linewidth=0.5,
                      label='avg 6 months',
                      linestyle='--')
        ax[i].annotate('{}'.format(int(avg6.amount)),
                       xy=(monthly_coffee.index[0], int(avg6.amount)),
                       xytext=(-10, 1),  # 3 points vertical offset
                       textcoords="offset points",
                       ha='right',
                       va='bottom',
                       color='blue')

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

        autolabel(bar, ax[i], el['amount'])
        i += 1

    # Remove unused plots
    for j in range(i, len(ax)):
        ax[j].set_axis_off()

    plt.tight_layout(w_pad=2.3, h_pad=1.3)
    return fig


def render_monthly_bar_stacked(_df_list):
    print("Render monthy spending on stack graph for all categories")
    fig, ax = plt.subplots(1, 1, figsize=(30, 15))

    bottom_value = 0
    for index, el in enumerate(_df_list):
        bar = ax.bar(el.index.values,
                     el['amount'],
                     color=colours[index],
                     label=el.name,
                     bottom=bottom_value,
                     width=150 * (1 / el.shape[0]))
        bottom_value += _df_list[index]['amount']

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


def render_average_pie(_df):
    print("Render average spending by category on pie chart")
    fig, ax = plt.subplots(1, 1, figsize=(30, 15))
    explodes = [0.0] * len(_df)
    explodes[0] = 0.2
    _, _, autotexts = ax.pie(_df['amount'], labels=_df['name'],
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
    data = organise_data_by_category(all_spending_df)
    monthly_groceries = extract_monthly_spending(data, GROCERIES)
    monthly_transport = extract_monthly_spending(data, TRANSPORT)
    monthly_restaurant = extract_monthly_spending(data, RESTAURANT)
    monthly_coffee = extract_monthly_spending(data, COFFEE)
    monthly_bar = extract_monthly_spending(data, BAR)
    monthly_misc = extract_monthly_spending(data, MISC)

    monthly_spending = [monthly_groceries, monthly_transport, monthly_restaurant,
                        monthly_coffee, monthly_bar, monthly_misc]

    figures.append(render_monthly_bar_by_cat(monthly_spending))
    figures.append(render_monthly_bar_stacked(monthly_spending))

    avg_df = df_tmp = pd.DataFrame(columns=['name', 'amount'])

    for cat in monthly_spending:
        _, _, average = compute_average(cat)
        avg_df = avg_df.append({'name': cat.name, 'amount': average}, ignore_index=True)

    figures.append(render_average_pie(avg_df))

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

