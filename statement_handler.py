#! /usr/bin/env python3

import os
import pandas as pd
import bank_name


def parse_statement(csv_file):
    """Parse the given statement and apply needed modification

    Args:
        csv_file (str): Path to csv file to parse

    Returns:
        pandas.core.frame.DataFrame: A parsed and organized dataframe for the given statement
    """

    if bank_name.SCOTIABANK in csv_file:
        return extract_scotiabank_cc(csv_file)
    elif bank_name.BMO in csv_file:
        return extract_bmo_cc(csv_file)
    else:
        raise("file type not handled")


# def extract_checking(csv_file):
#     checking = pd.read_csv(filepath_or_buffer=csv_file, sep=',', names=[ "date", "amount", "null", "type", "place" ], keep_default_na=False)
#     return checking


def extract_scotiabank_cc(csv_file):
    """Parse the given Scotiabank statement and apply needed modification

    Args:
        csv_file (str): Path to csv file to parse

    Returns:
        pandas.core.frame.DataFrame: A parsed and organized dataframe for the given statement
    """

    scotia_df = pd.read_csv(filepath_or_buffer=csv_file, sep=',', names=["date", "place", "amount"], keep_default_na=False)
    scotia_df['date'] = pd.to_datetime(scotia_df['date'], format='%m/%d/%Y', errors='coerce')
    scotia_df = remove_cc_income(scotia_df, bank_name.SCOTIABANK)
    if scotia_df.empty:
        print(f"It seems your CSV file content is either empty or does not contain any debit on your credit history. \
        \nPlease check the content of {os.path.basename(csv_file)}")
        return scotia_df
    scotia_df = spending_as_pos_value(scotia_df, bank_name.SCOTIABANK)

    return scotia_df


def extract_bmo_cc(csv_file):
    """Parse the given BMO statement and apply needed modification

    Args:
        csv_file (str): Path to csv file to parse

    Returns:
        pandas.core.frame.DataFrame: A parsed and organized dataframe for the given statement
    """

    bmo_df = pd.read_csv(filepath_or_buffer=csv_file, sep=',', usecols=[2, 4, 5], names=["date", "amount", "place"], keep_default_na=False)
    bmo_df['date'] = pd.to_datetime(bmo_df['date'], format='%Y%m%d', errors='coerce')
    bmo_df = remove_cc_income(bmo_df, bank_name.BMO)
    if bmo_df.empty:
        print(f"It seems your CSV file content is either empty or does not contain any debit on your credit history. \
        \nPlease check the content of {os.path.basename(csv_file)}")
        return bmo_df
    bmo_df = spending_as_pos_value(bmo_df, bank_name.BMO)
    return bmo_df


def remove_cc_income(credit_card_pd, bankName):
    """Remove the income entries from the credit card statement dataframe

    Args:
        credit_card_pd (pandas.core.frame.DataFrame): The dataframe to modify

    Returns:
        pandas.core.frame.DataFrame: A dataframe with all the income removed
    """

    print("Parsing: Remove income")
    if bankName == bank_name.SCOTIABANK:
        credit_card_pd = credit_card_pd[credit_card_pd.amount < 0]

    elif bankName == bank_name.BMO:
        credit_card_pd = credit_card_pd[credit_card_pd.amount > 0]

    return credit_card_pd


def spending_as_pos_value(credit_card_pd, bankName):
    """Make sure that the spending are listed as positive values

    Args:
        credit_card_pd (pandas.core.frame.DataFrame): The dataframe to modify

    Returns:
        pandas.core.frame.DataFrame: A dataframe with all the spending entries listed as positive value
    """

    print("Parsing: Spending as positive value")

    if bankName == bank_name.SCOTIABANK:
        credit_card_pd['amount'] = credit_card_pd['amount'].apply(lambda x: -x)
    elif bankName == bank_name.BMO:
        # BMO spendings are already in positive
        pass
    else:
        credit_card_pd['amount'] = credit_card_pd['amount'].apply(lambda x: -x)
    return credit_card_pd
