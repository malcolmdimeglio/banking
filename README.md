# banking

The overview.py python script is meant to give you a visual overview of your monthly spendings throughout the years. They are splited into categories like: Groceries, Transport, Restaurant, Coffee, Bar and Miscellaneous.

## How to use it
This document will assume that you have previously installed __python3__ as well as __pip3__.
This program has been tested on a MacOS environment. Further test will be conducted on a Linux environment.
I am also assuming your current working directory is this repository.

### Edit the script
As of today, file names are hardcoded and this will eventually change in order to allow more flexibility. But until then, you will need to open the `overview.py` file and edit the following lines (line 17-18) to match your environement:

```python
csv_file = "/Users/Malcolm/Desktop/pcbanking.csv"
output_pdf = "/Users/Malcolm/Desktop/mytest.pdf"
```

`csv_file` will be the file used by the script to parse your expenses and render them. The file HAS TO be a .csv file format and the data HAS TO be organised as such "date,place,amount". The comma is used as separator.

`output_pdf` will be the PDF file which will contain all graphs you need in order to have an idea of your expenses each months.

### Install dependencies
The file `requirements.txt` contains all the dependencies you will need to install in order for this program to work. Conveniently you can execute the following `pip3 install -r requirements.txt` and the installation will be handled for you

### Launch
To finish, in order to launch the script simply execute it with:
```bash
./overview.py
```

## How does it work?
### Read the .csv file
Depending on your banking institution the .csv file can look differently. I used what Scotiabank Canada is providing to me.
Here is an example of a raw CSV file provided by the Scotiabank
```text
5/21/2018,"MARKETPLACE IGA # 16     VANCOUVER    BC ",-7.36
5/21/2018,"TIM HORTONS #0335        KAMLOOPS     BC ",-2.51
5/24/2018,"LOCAL GASTOWN            VANCOUVER    BC ",-22.17
5/24/2018,"MARKETPLACE IGA # 16     VANCOUVER    BC ",-19.93
5/24/2018,"Amazon *Marketplce CA    WWW.AMAZON.CAON ",-36.15
5/25/2018,"CAR2GO                   855-454-1002 BC ",-4.35
5/25/2018,"CAR2GO                   855-454-1002 BC ",-3.64
5/26/2018,"CDN TIRE STORE #00389    VANCOUVER    BC ",-23.05
5/27/2018,"COMPASS VENDING          BURNABY      BC ",-20.00
5/27/2018,"JJ BEAN ON MAIN          VANCOUVER    BC ",-2.52
5/28/2018,"CREDIT VOUCHER/RETURN CAR2GO 855-454-1002 BC ",3.64
``` 
You can see that the field separator is a comma, and the data order is like such: date, location, amount.
The spendings appear as negative values and the "incomes" as positive.

### Is there a header?
In order to run through all the data efficiently we need the csv file to have a header before we parse the data.
The header that has been implemented is: `date,place,amount`
```python
with open(csv_file, 'r') as file:
    data = file.readline()  # read the first line
    if re.search(header, data):  # if header is present then do not modify the csv file
        do_modify = False
    else:
        do_modify = True
 ```
 This piece of code will determine if the previously mentioned header is already present in the csv file. If not present then the code following this snippet will insert it on the first line of the document. 
 
 ### Parsing the CSV
 After checking for the header the code proceeds to parse the csv file using Pandas:
 ``` python
 import pandas as pd
 
 all_spending_df = pd.read_csv(filepath_or_buffer=csv_file, sep=',')
 ```
We now have a dataframe with all the CSV data in it. The code will need to standardize those data by lowering all cases, removing all lines with positive amounts (incomes) since we're only interested in spendings, and convert the string dates into datetime format.
The data frame will then looks like such

```
  date      place                                     amount
0 2018-5-21,marketplace iga # 16     vancouver    bc ,-7.36
1 2018-5-21,tim hortons #0335        kamloops     bc ,-2.51
2 2018-5-24,local gastown            vancouver    bc ,-22.17
3 2018-5-24,marketplace iga # 16     vancouver    bc ,-19.93
4 2018-5-24,amazon *marketplce ca    www.amazon.caon ,-36.15
5 2018-5-25,car2go                   855-454-1002 bc ,-4.35
6 2018-5-25,car2go                   855-454-1002 bc ,-3.64
7 2018-5-26,cdn tire store #00389    vancouver    bc ,-23.05
8 2018-5-27,compass vending          burnaby      bc ,-20.00
9 2018-5-27,jj bean on main          vancouver    bc ,-2.52
...
```

### Organising the data
Now we need to organise the data into categories, so that the rendering makes more sense. In order to dispatch all spendings in the right category some key words are used in order to differenciate them all.

You will find the list of keyword at the begining of the script
```python
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
```

Those lists will grow in time as more places are visited.

If we look at the data frame earlier displayed. The first spending displays: 
```
0 2018-5-21,marketplace iga # 16     vancouver    bc ,-7.36
```
After looking into the `place` field of the dataframe, we see `marketplace iga # 16     vancouver    bc `, looking at the lists above we can see that in the list `Groceries` we have the keyword `iga` The code will so put this expense in the Grocery dataframe `df_groc`.

The second line shows:
```
1 2018-5-21,tim hortons #0335        kamloops     bc ,-2.51
```
Which we can connect the `place` field to the key word `tim hortons` in the `Coffee` list.
And so on...


Each category will have its own dataframe. However, it is up to 3 times faster to populate dictionaries and then create a dataframe out of them, than creating empty dataframes and appending rows one after the other.
```python
dic_groc, dic_trans, dic_rest, dic_coffee, \
        dic_bar, dic_misc = {}, {}, {}, {}, {}, {}
g, t, r, c, b, m = [0]*6  # indexes
```

As an example for the *groceries* category: for each row we check via `is_row_in_category()` if the place mentioned is part of the list Groceries, just listed above. If yes, then let's create a new entry in the dictionary with the key being an index incrementing each time, and the value being the row we're currently looking at.
```python
for index, row in my_dataframe.iterrows():
        if is_row_in_category(row, Groceries):
            dic_groc[g] = row
            g = g+1
            continue
```

If the `place` field doesn't match with any keyword of any category then the spending will go into the misc category.

After parsing all the spendings, we will get 6 different dataframes for 6 categories (Groceries, Transport, Restaurant, Coffee, Bar and Misc) that we'll create the dataframes and store them store in a dictionary:

``` python
GROCERIES = 'groceries'
TRANSPORT = 'transport'
RESTAURANT = 'restaurant'
COFFEE = 'coffee'
BAR = 'bar'
MISC = 'misc'

df_groc = pd.DataFrame.from_dict(dic_groc, orient='index', columns=['date', 'place', 'amount'])
df_trans = pd.DataFrame.from_dict(dic_trans, orient='index', columns=['date', 'place', 'amount'])
...
df_misc = pd.DataFrame.from_dict(dic_misc, orient='index', columns=['date', 'place', 'amount'])

all_df = {
    GROCERIES: df_groc,
    TRANSPORT: df_trans,
    RESTAURANT: df_rest,
    COFFEE: df_coffee,
    BAR: df_bar,
    MISC: df_misc
}
```
Now we have a dictionnary of dataframe to work with
```python
data = organise_data_by_category(all_spending_df)
```
### Extract monthly spending by category
Now that we have everything well categorised, we want to know how much we spent per month per category.
```python
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
```
In order to avoid having padding 0s at the beggining and the end of the dataframe we had to take into account when was the first spending and when was the last. As an example:
* Your first spending is on November 12th 2016
* Your last spending is on February 26th 2018

Since we'll be looping on every month from Jan to Dec. We will get unecessary 0s from Jan 2016 to Oct 2016 as well as from March 2018 to Dec 2018. This can potentially make the rendering harder to read as we would not know if we didn't spend anything in that category for the said month because we saved money or because there was no data due to no credit card.

This snippet allows us to take this into consideration
```python
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
```

Now we can parse the dataframe and sum all expenses per month, each month every year
```python
for month in range(start_month, end_month + 1):
        df_temp = df_temp.append({"date": "{}-{}".format(month, year),
                                 "amount": _df[spending].loc[(_df[spending].date.dt.month == month) &
                                                             (_df[spending].date.dt.year == year), 'amount'].sum()},
                                 ignore_index=True)
```
Now we have a dataframe that contains a summary of all expenses per month for a specific category
```python
monthly_groceries = extract_monthly_spending(data, GROCERIES)
monthly_transport = extract_monthly_spending(data, TRANSPORT)
monthly_restaurant = extract_monthly_spending(data, RESTAURANT)
monthly_coffee = extract_monthly_spending(data, COFFEE)
monthly_bar = extract_monthly_spending(data, BAR)
monthly_misc = extract_monthly_spending(data, MISC)

monthly_spending = [monthly_groceries, monthly_transport, monthly_restaurant,
                    monthly_coffee, monthly_bar, monthly_misc]
```
### Rendering
Each graph, plot or pie chart use the same color code. So that you can visually easily compare different kind of graphs as each category will have a consistent color.
```python
colours = ['#5DADE2',  # blue
           '#F5B041',  # orange
           '#58D68D',  # green
           '#EC7063',  # red
           '#BB8FCE',  # purple
           '#808B96',  # grey
           '#F7DC6F']  # yellow
```
The library used for rendering those graphs is matplotlib
```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
```
#### Bar chart per category per month
![Bar charts](https://github.com/malcolmdimeglio/banking/blob/master/img/all_bar_chart.png)
It's been decided, for easy reading purposes, that the rendering would disply only rows of 3 graph per row. As it seems that on a page document, adding more than 3 graph on the same line would reduce readibility drastically.
The snippet of code below shows how the bar chart will be displayed.
* X axis: date (scale: 1 month)
* Y axis: $ spent
* color: 1 color per category
* width: bit of a dark magic trick here found on a forum. Since the width has to be a number between 0 and 1 but is based on the X axis scale. Which is in our case, 1 month in a datetime format.
```python
for el in _df_list:
    bar = ax[i].bar(el.index.values,
                    el['amount'],
                    color=colours[i],
                    label='monthly',
                    width=150 * (1 / el.shape[0]))
 ```
 Each graph displays an horizontal red line representing the average spending per month for that category over all time spending. In blue, is displayed the average over the last 6 months. This allows to get an idea if we happened to spend more than usual on a specific month. The average is computed by: 
 * Ommiting the current month. Since it's highly likely that there will be more expenses happening. Therefore the value might throw the computation off
 * Omitting the extremums. The maximum and minum spending ever recorded are not representative of the average and sometimes can tottaly give a false impression.
 * Omitting all $0 months as they are most likely due to a lack of data and not an extrem show of self restraint.
 * When computing the average over the last 6 months, first, we get rid of all expenses older than 6 months then, we remove the min and max spending months
 
 The `compute_average()` method allows an optional parametter *period_months* defaulted to 0. Any positive value represent how far back (in months) should we go to compute the average spending.
 ```python
 if period_months > 0:
      from_date = today - pd.DateOffset(months=int(period_months))
      _df = _df.drop(_df[_df.index < pd.to_datetime(from_date)].index)

_df = _df.drop(_df[_df.amount == _df.amount.max()].index)
_df = _df.drop(_df[_df.amount == _df.amount.min()].index)
_df = _df.drop(_df[(_df.index.month == today.month) & (_df.index.year == today.year)].index)
_df = _df.drop(_df[_df.amount == 0].index)

return _df.min(), _df.max(), _df.mean()
```
![Bar charts](https://github.com/malcolmdimeglio/banking/blob/master/img/compute_average.png)
 
After computing the average we display the horizontal line with:
```python
ax[i].axhline(y=int(avg.amount),
              color="red",
              linewidth=0.5,
              label='avg',
              linestyle='--')

ax[i].axhline(y=int(avg6.amount),
              color="blue",
              linewidth=0.5,
              label='avg 6 months',
              linestyle='--')
```

![Bar charts](https://github.com/malcolmdimeglio/banking/blob/master/img/groceries_bar_chart.png)


And we write it's value on the Y axis for easier readibility
```python
ax[i].annotate('{}'.format(int(avg.amount)),
               xy=(monthly_coffee.index[0], int(avg.amount)),
               xytext=(-10, 1),  # 3 points vertical offset
               textcoords="offset points",
               ha='right',
               va='bottom',
               color='red')
```
![Bar charts](https://github.com/malcolmdimeglio/banking/blob/master/img/display_avg.png)

For readability purposes each graph displays on top of each bar(*rects*) the value it's plotting. Since we can get a lot of data, this option was the more readable one.
* _height_: represent the amounts spent each month
* _rects_: represent the bars ploted for each month 
```python
def autolabel(rects, ax, height):
  for index, rect in enumerate(rects):
      ax.annotate('{}'.format(int(height[index])),
                  xy=(rect.get_x() + rect.get_width() / 2, height[index]),
                  xytext=(0, 1),  # 1 points vertical offset
                  textcoords="offset points",
                  ha='center',
                  va='bottom')
```
![Bar charts](https://github.com/malcolmdimeglio/banking/blob/master/img/bar_values.png)

#### Stacked bar chart of all categories per month
The stacked chart shows the same information as the 6 bar charts from the previous section. However, by stacking all spending of all categories of the same month together, we can extrapolate the overtime spending tendency.
![Bar charts](https://github.com/malcolmdimeglio/banking/blob/master/img/stacked_bar_chart.png)
The logic here is to simply execute the same as for the single category bar char per graph (see above). But, in this case, instead of starting to plot on another graph when displaying the new category, we use the same figure and offset the bottom by the value ploted previously for the previous category.
```python
bottom_value = 0
    for index, el in enumerate(_df_list):
        bar = ax.bar(el.index.values,
                     el['amount'],
                     color=colours[index],
                     label=el.name,
                     bottom=bottom_value,
                     width=150 * (1 / el.shape[0]))
        bottom_value += _df_list[index]['amount']
 ```
#### Pie chart of average spending per category
![Bar charts](https://github.com/malcolmdimeglio/banking/blob/master/img/pie_chart.png)
This chart allows to see the proportion each category has compared to the overall spending.
The dev logic behind this pie chart is exactly the same as the previous chart explained above, except the 
```python
_, _, autotexts = ax.pie(_df['amount'], labels=_df['name'],
                         explode=explodes,
                         autopct='%1.1f%%',
                         shadow=False,
                         frame=False,
                         startangle=90,
                         colors=colours,
                         textprops={'fontsize': 'xx-large'},
                         wedgeprops={'linewidth': 1, 'edgecolor': "black"})
```
The explode argument we can see above recieves a list of float as parameter. The list must be as long as the number of category polted in the pie chart. 
The float value represents how much the correspondig pie piece is being "exploded" or pulled out of the pie.
0.2 has been arbitrarily selected after a few visual tests.
```python
explodes = [0.0] * len(_df)
explodes[0] = 0.2
```
