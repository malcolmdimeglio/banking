#! /usr/bin/env python3

import sys
import os
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import category_name
import render
import statement_handler as sh
import organizer

# To get rid of pandas' matplotlib "FutureWarning"
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

credit_card_statement_folder = os.path.dirname(os.path.abspath(__file__)) + "/statements/CreditCard"
checking_account_statement_folder = os.path.dirname(os.path.abspath(__file__)) + "/statements/Checking"
output_pdf = os.path.dirname(os.path.abspath(__file__)) + "/overview.pdf"


if __name__ == "__main__":
    # Let's handle the potential debug parameters first
    if len(sys.argv) >= 2 and sys.argv[1].lower() == "debug":
        print("\n--- DEBUG ---")
        debug_pd = []
        if len(sys.argv) >= 3:
            for arg in sys.argv[2:]:
                l_arg = arg.lower()
                if l_arg == category_name.GROCERIES \
                        or l_arg == category_name.TRANSPORT \
                        or l_arg == category_name.RESTAURANT \
                        or l_arg == category_name.COFFEE \
                        or l_arg == category_name.BAR \
                        or l_arg == category_name.MISC \
                        or l_arg == category_name.BILLS:
                    debug_pd.append(l_arg)
                elif l_arg == "all":  # if all then redefine everything and exit the loop. So that we don't have doubles
                    debug_pd = [category_name.GROCERIES, category_name.TRANSPORT, category_name.RESTAURANT, category_name.COFFEE, category_name.BAR, category_name.MISC, category_name.BILLS]
                    break
                else:
                    print(f" '{arg}' Unknown parameter. Parameter accepted are: groceries, transport, restaurant, coffee, bar, misc, all")
                    print("i.e: ./overview debug bar coffee")
                    exit()
        else:
            debug_pd.append("misc")

    # Verify hard codded output pdf path
    if not (os.path.exists(os.path.dirname(output_pdf))):
        print(f"Could not access {os.path.dirname(output_pdf)} to output the results. Please verify path syntax")
        sys.exit()
    try:
        tmp_list_credit_card = []
        for file in os.listdir(credit_card_statement_folder):
            if file.lower().endswith('.csv'):
                csv_credit_card_file = credit_card_statement_folder + '/' + file
                print(f"Read CSV file {file}...")
                # Extract csv into dataframe, handle each bank statement accordingly
                tmp_list_credit_card.append(sh.parse_statement(csv_credit_card_file))
    except FileNotFoundError:
        print('** ERROR ** File {} not found'.format(csv_credit_card_file))
        sys.exit()

    all_spending_df = pd.concat(tmp_list_credit_card, axis=0, ignore_index=True, sort=False)

    # credit_card_data = organise_data_by_category(credit_card_spending_df)
    all_data = organizer.organise_data_by_category(all_spending_df)

    monthly_groceries = organizer.extract_monthly_spending_by_category(all_data, category_name.GROCERIES)
    monthly_transport = organizer.extract_monthly_spending_by_category(all_data, category_name.TRANSPORT)
    monthly_restaurant = organizer.extract_monthly_spending_by_category(all_data, category_name.RESTAURANT)
    monthly_coffee = organizer.extract_monthly_spending_by_category(all_data, category_name.COFFEE)
    monthly_bar = organizer.extract_monthly_spending_by_category(all_data, category_name.BAR)
    monthly_misc = organizer.extract_monthly_spending_by_category(all_data, category_name.MISC)
    monthly_bills = organizer.extract_monthly_spending_by_category(all_data, category_name.BILLS)

    transport_data = organizer.organise_transport_by_sub_cat(all_data[category_name.TRANSPORT])
    monthly_transport_carshare = organizer.extract_monthly_spending_by_category(transport_data, category_name.TR_CARSHARE)
    monthly_transport_rental = organizer.extract_monthly_spending_by_category(transport_data, category_name.TR_RENTAL)
    monthly_transport_cab = organizer.extract_monthly_spending_by_category(transport_data, category_name.TR_CAB)
    monthly_transport_translink = organizer.extract_monthly_spending_by_category(transport_data, category_name.TR_TRANSLINK)
    monthly_transport_misc = organizer.extract_monthly_spending_by_category(transport_data, category_name.TR_MISC)
    monthly_transport_car = organizer.extract_monthly_spending_by_category(transport_data, category_name.TR_CAR)

    monthly_spending = [monthly_bills, monthly_groceries, monthly_transport, monthly_restaurant,
                        monthly_coffee, monthly_bar, monthly_misc]

    monthly_transport = [monthly_transport_carshare, monthly_transport_rental, monthly_transport_cab, monthly_transport_translink, monthly_transport_car]  # not interested about misc

    figures = []
    figures.append(render.monthly_bar_by_cat(monthly_spending[1:]))  # Do not plot bills expenses
    figures.append(render.monthly_bar_stacked(monthly_spending))
    figures.append(render.average_pie(monthly_spending))
    figures.append(render.monthly_bar_by_cat(monthly_transport, useAbsoluteAvg=True))
    # figures.append(render_monthly_bar_stacked(monthly_transport, useAbsoluteAvg=True, title="Month by month transport"))

    doc = PdfPages(output_pdf)
    for figure in figures:
        figure.savefig(doc, format='pdf')
    doc.close()
    print("Output PDF document: {}".format(output_pdf))

    if "debug_pd" in locals() and len(debug_pd) > 0:
        for el in debug_pd:
            print(f"Content of {el} dataframe")
            with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                print(all_data[el].sort_values(by=['date']).to_string(index=False))
                print()
