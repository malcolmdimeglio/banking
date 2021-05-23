#! /usr/bin/env python3

import re
import pandas as pd
from datetime import date
import category
import category_name


def is_row_in_category(row, categories):
    """Determines if row['place'] is in the given category

    Args:
        row (pandas.core.series.Series): Single row [date,place,amount] of a dataframe
        category (list): Category list

    Returns:
        bool: True if row in category, False otherwise
    """

    for place in categories:
        if re.search(place, row['place'], re.IGNORECASE):
            return True
    return False


def organise_data_by_category(my_dataframe):
    """Parse all spending and populate smaller dataframes by categories

    Args:
        my_dataframe (pandas.core.frame.DataFrame): my_dataframe  Unparsed dataframe with all uncategorized expenses

    Returns:
        dict: A dictionary of dataframe. [key] = category name; [value] = dataframe with the all categorie's related expenses
    """

    print("Organise spendings into categories")

    # it is 3 times faster to create a dataframe from a full dictionary rather than appending rows after rows to an already existing dataframe
    dic_groc, dic_trans, dic_rest, dic_coffee, dic_bar, dic_misc, dic_bills = {}, {}, {}, {}, {}, {}, {}
    g, t, r, c, b, m, f = [0] * 7  # indexes

    # Let's go over each rows of the unsorted dataframe and populate the category's dictionary.
    for _, row in my_dataframe.iterrows():
        if is_row_in_category(row, category.Groceries):
            dic_groc[g] = row
            g = g + 1
            continue

        if is_row_in_category(row, category.Transport):
            dic_trans[t] = row
            t = t + 1
            continue

        if is_row_in_category(row, category.Restaurant):
            dic_rest[r] = row
            r = r + 1
            continue

        if is_row_in_category(row, category.Coffee):
            dic_coffee[c] = row
            c = c + 1
            continue

        if is_row_in_category(row, category.Bar):
            dic_bar[b] = row
            b = b + 1
            continue

        if is_row_in_category(row, category.Bills):
            dic_bills[f] = row
            f = f + 1
            continue

        # If none of the above then let's put it in misc spending
        dic_misc[m] = row
        m = m + 1

    df_groc = pd.DataFrame.from_dict(dic_groc, orient='index', columns=['date', 'place', 'amount'])
    df_trans = pd.DataFrame.from_dict(dic_trans, orient='index', columns=['date', 'place', 'amount'])
    df_rest = pd.DataFrame.from_dict(dic_rest, orient='index', columns=['date', 'place', 'amount'])
    df_coffee = pd.DataFrame.from_dict(dic_coffee, orient='index', columns=['date', 'place', 'amount'])
    df_bar = pd.DataFrame.from_dict(dic_bar, orient='index', columns=['date', 'place', 'amount'])
    df_misc = pd.DataFrame.from_dict(dic_misc, orient='index', columns=['date', 'place', 'amount'])
    df_bills = pd.DataFrame.from_dict(dic_bills, orient='index', columns=['date', 'place', 'amount'])

    all_df = {
        category_name.GROCERIES: df_groc,
        category_name.TRANSPORT: df_trans,
        category_name.RESTAURANT: df_rest,
        category_name.COFFEE: df_coffee,
        category_name.BAR: df_bar,
        category_name.MISC: df_misc,
        category_name.BILLS: df_bills
    }

    return all_df


def organise_transport_by_sub_cat(_dfTransport):
    """Parse all spending in transport and populate smaller dataframes by categories

    Args:
        _dfTransport (pandas.core.frame.DataFrame): Unparsed dataframe with all transport expenses

    Returns:
        [dict: A dictionary of dataframe. [key] = category name; [value] = dataframe with the all categorie's related expenses
    """

    # it is 3 times faster to create a dataframe from a full dictionary rather than appending rows after rows to an already existing dataframe
    dic_carshare, dic_rental, dic_cab, dic_translink, dic_misc, dic_car = {}, {}, {}, {}, {}, {}
    csh, r, c, t, m, car = [0] * 6  # indexes

    # Let's go over each rows of the unsorted dataframe and populate the category's dictionary.
    for _, row in _dfTransport.iterrows():
        if is_row_in_category(row, category.TransportCarShare):
            dic_carshare[csh] = row
            csh = csh + 1
            continue
        if is_row_in_category(row, category.TransportRental):
            dic_rental[r] = row
            r = r + 1
            continue
        if is_row_in_category(row, category.TransportCab):
            dic_cab[c] = row
            c = c + 1
            continue
        if is_row_in_category(row, category.TransportTranslink):
            dic_translink[t] = row
            t = t + 1
            continue
        if is_row_in_category(row, category.TransportMisc):
            dic_misc[m] = row
            m = m + 1
            continue
        if is_row_in_category(row, category.TransportCar):
            dic_car[car] = row
            car = car + 1
            continue

        # If none of the above then let's put it in misc spending
        dic_misc[m] = row
        m = m + 1

    df_carshare = pd.DataFrame.from_dict(dic_carshare, orient='index', columns=['date', 'place', 'amount'])
    df_rental = pd.DataFrame.from_dict(dic_rental, orient='index', columns=['date', 'place', 'amount'])
    df_cab = pd.DataFrame.from_dict(dic_cab, orient='index', columns=['date', 'place', 'amount'])
    df_translink = pd.DataFrame.from_dict(dic_translink, orient='index', columns=['date', 'place', 'amount'])
    df_misc = pd.DataFrame.from_dict(dic_misc, orient='index', columns=['date', 'place', 'amount'])
    df_car = pd.DataFrame.from_dict(dic_car, orient='index', columns=['date', 'place', 'amount'])

    allTransport_df = {
        category_name.TR_CARSHARE: df_carshare,
        category_name.TR_RENTAL: df_rental,
        category_name.TR_CAB: df_cab,
        category_name.TR_TRANSLINK: df_translink,
        category_name.TR_MISC: df_misc,
        category_name.TR_CAR: df_car
    }

    return allTransport_df


def extract_monthly_spending_by_category(_df, categoryName):
    """Sumarize for each month the total spending for a given category

    Args:
        _df (dict): An organized by category dataframe
        categoryName (str): The category name you want to extract the information of

    Returns:
        [type]: A dataframe with only 1 category's information and the sum of all the spendings for that category, listed by month
    """

    print("Extract monthly spendings for {}".format(categoryName))
    df_temp = pd.DataFrame(columns=['date', 'amount'])

    if _df[categoryName].empty:
        df_temp.name = categoryName
        return df_temp

    if categoryName == category_name.BILLS:
        df_rent = pd.DataFrame(columns=['date', 'amount'])
        df_icbc = pd.DataFrame(columns=['date', 'amount'])

    # let's only do the math between the first and last spending day in the csv file to avoid
    # blank values at the begining and the end of the charts

    # max_year = credit_card_spending_df['date'].max().year
    max_year = date.today().year
    max_month = date.today().month

    mindate = date.today()  # to find the minimum date, let's start with mini = the maximum possible (aka today)
    for el in _df.values():
        mindate = min(mindate, el['date'].min())
    min_year = mindate.year
    min_month = mindate.month

    for year in range(min_year, max_year + 1):
        # Avoid 0 padding at the beginning and the end of the graph
        start_month = 1 if year > min_year else min_month
        end_month = 12 if year < max_year else max_month

        start_month = min_month if year == min_year else 1
        end_month = max_month if year == max_year else 12

        # sum all spending from a whole month, each month of the year
        for month in range(start_month, end_month + 1):
            df_temp = df_temp.append({"date": pd.to_datetime("{}-{}".format(month, year)),
                                     "amount": _df[categoryName].loc[(_df[categoryName].date.dt.month == month) &
                                                                     (_df[categoryName].date.dt.year == year), 'amount'].sum()},
                                     ignore_index=True)

            if categoryName == category_name.BILLS:
                # Handle rent
                rent = 0
                if year == 2018 and month < 12:
                    rent = 1000
                if (year == 2018 and month == 12) or year == 2019 or (year == 2020 and month <= 9):
                    rent = 1550
                if (year == 2020 and month >= 10) or year > 2020:
                    rent = 1750
                if rent > 0:
                    df_rent = df_rent.append({"date": pd.to_datetime("{}-{}".format(month, year)), "amount": rent},
                                             ignore_index=True)
                # Handle ICBC
                if (year == 2020 and month >= 11) or (year == 2021 and month <= 6):
                    df_icbc = df_icbc.append({"date": pd.to_datetime("{}-{}".format(month, year)), "amount": 96},
                                             ignore_index=True)

    if categoryName == category_name.BILLS:  # Add rent to bills
        df_rent.set_index('date', inplace=True)
        df_icbc.set_index('date', inplace=True)

        # append all fixed expenses. Some indexes might duplicate
        df_bills = df_rent.append(df_icbc)
        # Since some expenses may overlap, let's sum all the amounts from the ones that have the same index (month)
        df_temp = df_bills.groupby(df_bills.index)['amount'].sum().reset_index()

    df_temp.name = categoryName
    df_temp.set_index('date', inplace=True)

    return df_temp
