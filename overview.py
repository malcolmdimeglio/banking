#! /usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import re
from datetime import date
import matplotlib.dates as mdates

csv_file = "/Users/Malcolm/Desktop/pcbanking.csv"
header = "date,place,amount"

Groceries = ["iga", "save on foods", "nesters", "t&t", "kiki", "yig", "persia foods"]
Transport = ["car2go", "evo", "avis", "rentals", "petrocan", "husky", "esso[^a-z]", "super save", "cab",
             "compass", "taxi", "shell"]
Restaurant = ["doordash", "skipthedishes", "restau", "a&w", "cuisine",
              "moxie's", "burger", "la belle patate", "pho", "pizza", "bestie",
              "kitchen", "thai", "el camino's", "grill", "ice cream", "japanese",
              "kaori izakaya", "taco", "mexican", "zipang provisions", "mr. steak", "poke", "sushi", "earls"
              "mcdonald's", "diner", "subway sandwiches", "falafel", "donair", "fish", "pizz", "poutine",
              "white spot", "vij's", "the capital", "cactus club", "cantina", "fork", "denny's", "mumbai local"
              "freshii", "captain's boil", "korean"]
Coffee = ["cafe", "coffee", "tim hortons", "starbucks", "bean", "birds & the beets", "the mighty oak",
          "le marche st george", "caffe", "coco and olive", "buro", "blenz", "green horn", "bakery", "a & w"]
Bar = ["brew", "beer", "pub[^a-z]", "steamworks", "distillery", "bar[^a-z]", "narrow lounge", "rumpus room",
       "five point", "score on davie", "tap & barrel", "the cambie", "colony", "alibi room"]
Fixed = ["ymca", "shaw", "fido", "soundcloud", "per se social corner", "grapes & soda"]

GROCERIES = 'groceries'
TRANSPORT = 'transport'
RESTAURANT = 'restaurant'
COFFEE = 'coffee'
BAR = 'bar'
FIX = 'fix'
MISC = 'misc'

ALL = Groceries + Transport + Restaurant + Coffee + Bar + Fixed


# prepend header to csv
with open(csv_file, 'r') as file:
    data = file.readline()
    if re.search(header, data):
        do_modify = False
    else:
        do_modify = True

with open(csv_file, 'r') as file:
    data = file.read()

if do_modify:
    with open(csv_file, 'w') as file:
        file.write(header + '\n' + data)

# Extract csv into dataframe
all_spending_df = pd.read_csv(filepath_or_buffer=csv_file, sep=',')

# Remove all incomes
all_spending_df = all_spending_df[all_spending_df.amount < 0]

# Change spending into positive values and lower case the place column
all_spending_df['amount'] = all_spending_df['amount'].apply(lambda x: -x)
all_spending_df['place'] = all_spending_df["place"].apply(lambda x: x.lower())
all_spending_df['date'] = pd.to_datetime(all_spending_df['date'])


# Extract the Misc spending (prob a nicer way to do that)
def is_row_in_category(my_row, my_list):
    for el in my_list:
        if re.search(el, my_row['place']):
            return True
    return False


def populate(_df, row):
    _df = _df.append({'date': row['date'],
                      'place': row['place'],
                      'amount': row['amount']},
                     ignore_index=True)
    return _df


def organise_data(my_dataframe):
    df_groc = df_trans = df_rest = df_coffee = \
    df_bar = df_fixed = df_misc = pd.DataFrame(columns=['date', 'place', 'amount'])

    for index, row in my_dataframe.iterrows():
        if is_row_in_category(row, Groceries):
            df_groc = populate(df_groc, row)
            continue

        if is_row_in_category(row, Transport):
            df_trans = populate(df_trans, row)
            continue

        if is_row_in_category(row, Restaurant):
            df_rest = populate(df_rest, row)
            continue

        if is_row_in_category(row, Coffee):
            df_coffee = populate(df_coffee, row)
            continue

        if is_row_in_category(row, Bar):
            df_bar = populate(df_bar, row)
            continue

        if is_row_in_category(row, Fixed):
            df_fixed = populate(df_fixed, row)
            continue

        # If none of the above then let's put it in misc spending
        df_misc = populate(df_misc, row)

    all_df = {
        GROCERIES: df_groc,
        TRANSPORT: df_trans,
        RESTAURANT: df_rest,
        COFFEE: df_coffee,
        BAR: df_bar,
        FIX: df_fixed,
        MISC: df_misc
    }

    return all_df


def extract_monthly_spending(_df, spending):
    df_tmp = pd.DataFrame(columns=['date', 'amount'])

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

        # sum all spendings from a whole month, each month of the year
        for month in range(start_month, end_month + 1):
            df_tmp = df_tmp.append({"date": "{}-{}".format(month, year),
                                    "amount": _df[spending].loc[(_df[spending].date.dt.month == month) & \
                                                                (_df[spending].date.dt.year == year), 'amount'].sum()},
                                   ignore_index=True)

    df_tmp['date'] = pd.to_datetime(df_tmp['date'])
    df_tmp.set_index('date', inplace=True)
    df_tmp.name = spending

    return df_tmp


def autolabel(rects, ax):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(int(height)),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


def compute_average(_df):
    today = date.today()
    df_tmp = pd.DataFrame(columns=['date', 'amount'])
    df_tmp = _df

    df_tmp = df_tmp.drop(df_tmp[df_tmp.amount == df_tmp.amount.max()].index)
    df_tmp = df_tmp.drop(df_tmp[df_tmp.amount == df_tmp.amount.min()].index)
    df_tmp = df_tmp.drop(df_tmp[(df_tmp.index.month == today.month) & (df_tmp.index.year == today.year)].index)

    return df_tmp.min(), df_tmp.max(), df_tmp.mean()


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
        bar = ax[i].bar(el.index.values,
                        el['amount'],
                        color=colours[i],
                        label='monthly',
                        width=150 * (1 / el.shape[0]))

        # Plot the average monthly spending on the corresponding graph
        _, _, avg = compute_average(el)
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

        # 45 deg angle for X labels
        plt.setp(ax[i].get_xticklabels(),
                 rotation=45,
                 ha="right")

        # Add XY labels
        ax[i].set(xlabel="Date",
                  ylabel="Spending ($)")
        ax[i].title.set_weight('extra bold')
        ax[i].title.set_fontsize('x-large')
        ax[i].title.set_text("{} spending".format(el.name))

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


def render_monthly_bar_total(_df_list):
    fig, ax = plt.subplots(1, 1, figsize=(30, 15))

    bottomV = 0
    for index, el in enumerate(_df_list):
        bar = ax.bar(el.index.values,
                     el['amount'],
                     color=colours[index],
                     label=el.name,
                     bottom=bottomV,
                     width=150 * (1 / el.shape[0]))
        bottomV += _df_list[index]['amount']

    autolabel(bar, ax, bottomV)

    # 45 deg angle for X labels
    plt.setp(ax.get_xticklabels(),
             rotation=45,
             ha="right")

    # Add XY labels
    ax.set(xlabel="Date",
           ylabel="Spending ($)")
    ax.title.set_weight('extra bold')
    ax.title.set_fontsize('x-large')
    ax.title.set_text("Month by month spending")

    # Set the locator
    locator = mdates.MonthLocator()  # every month
    # Specify the format - %b gives us Jan, Feb...
    fmt = mdates.DateFormatter('%b %Y')

    ax.xaxis.set_major_locator(locator)
    # Specify formatter
    ax.xaxis.set_major_formatter(fmt)
    ax.legend()

    plt.tight_layout(w_pad=2.3, h_pad=1.3)
    return fig


if __name__ == "__main__":
    data = organise_data(all_spending_df)
    monthly_groceries = extract_monthly_spending(data, GROCERIES)
    monthly_transport = extract_monthly_spending(data, TRANSPORT)
    monthly_restaurant = extract_monthly_spending(data, RESTAURANT)
    monthly_coffee = extract_monthly_spending(data, COFFEE)
    monthly_bar = extract_monthly_spending(data, BAR)
    monthly_misc = extract_monthly_spending(data, MISC)
