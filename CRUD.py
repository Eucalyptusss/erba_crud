


"""
CRUD SYSTEM Version 1.0
Vincent Welsh
Jan 20th, 2022

The purpose of this system is to provide seamless inventory and pricing analysis.
"""


###################################################################################################
########################################  IMPORTS  ################################################
###################################################################################################

from asyncio import SubprocessTransport
import os
from re import sub
#from types import NoneType
import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_daq as daq
from pandas.core.arrays import integer
from pandas.io.formats import style
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from scipy import stats
import numpy as np
from datetime import date



recipes = pd.read_csv('/Users/johnwelsh/Desktop/ERBA-CRUD/recipe_list.csv')
external_stylesheets = [dbc.themes.BOOTSTRAP]
# Create an app.
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.scripts.config.serve_locally = True
app.config.suppress_callback_exceptions = True

#app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()],
 #                   external_stylesheets=external_stylesheets)
# Create an app.
app.title = 'CRUD App'

num_products = 1
###################################################################################################
########################################  FUNCTIONS  ##############################################
###################################################################################################

def determine_highest_cpm(og_cpm, new_cpm):
    """
    Funtion to detemine highest cost per measurement
    """
    if og_cpm > new_cpm:
        return og_cpm
    else:
        return new_cpm

def get_num_products():
    global num_products
    return num_products

def set_num_products(n):
    global num_products
    num_products = n

def get_inventory_table():
    """
    Returns data stored in the master inventory csv file
    """
    df = pd.read_csv('/Users/johnwelsh/Desktop/ERBA-CRUD/inventory_master_file.csv')
    table = dbc.Table.from_dataframe(
            df, striped=True, bordered=True, hover=True
        )
    return table
def get_product_table():
    """
    Returns data stored in the master inventory csv file
    """
    df = pd.read_csv('/Users/johnwelsh/Desktop/ERBA-CRUD/product_master_file.csv')
    table = dbc.Table.from_dataframe(
            df, striped=True, bordered=True, hover=True
        )
    return table
def get_order_table():
    """
    Returns data stored in the master inventory csv file
    """
    df = pd.read_csv('/Users/johnwelsh/Desktop/ERBA-CRUD/order_master_file.csv')
    table = dbc.Table.from_dataframe(
            df, striped=True, bordered=True, hover=True
        )
    return table

def get_inventory_df():
    """
    Returns data stored in the master inventory csv file
    """
    df = pd.read_csv('/Users/johnwelsh/Desktop/ERBA-CRUD/inventory_master_file.csv')
    return df
def get_product_df():
    """
    Returns data stored in the master inventory csv file
    """
    df = pd.read_csv('/Users/johnwelsh/Desktop/ERBA-CRUD/product_master_file.csv')
    return df
def get_order_df():
    """
    Returns data stored in the master inventory csv file
    """
    df = pd.read_csv('/Users/johnwelsh/Desktop/ERBA-CRUD/order_master_file.csv')
    return df

def update_inventory_file(df):
    """
    Updates data stored in the master inventory csv file
    """
    df.to_csv('/Users/johnwelsh/Desktop/ERBA-CRUD/inventory_master_file.csv', index=False)

def update_product_file(df):
    """
    Updates data stored in the master inventory csv file
    """
    df.to_csv('/Users/johnwelsh/Desktop/ERBA-CRUD/product_master_file.csv', index = False)
    
def update_order_file(df):
    """
    Updates data stored in the master inventory csv file
    """
    df.to_csv('/Users/johnwelsh/Desktop/ERBA-CRUD/order_master_file.csv')
    

def calculate_profit(list_of_products, quantity_of_products, sell_price):
    profit = 0
    gross_total = 0
    product_df = pd.read_csv('/Users/johnwelsh/Desktop/ERBA-CRUD/product_master_file.csv')
    idx = 0
    for product in list_of_products:
        if type(quantity_of_products) == list:
            amount_ordered = quantity_of_products[idx]
        else:
            amount_ordered = quantity_of_products
        if type(sell_price) == list:
            gross = sell_price[idx]*amount_ordered
        else:
            gross = gross = sell_price*amount_ordered

        profit += gross - (product_df.loc[product_df['Product Name'] == product]['Individual Cost']
                           .mean()*amount_ordered)
        gross_total += gross
        idx += 1
    return profit, gross_total

def update_product_table(list_of_products, quantity_of_products):
    pro_df = get_product_df()
    if type(quantity_of_products) == list:

        zip_object = zip(list_of_products, quantity_of_products)
        for product, quantity in zip_object:
            idx = pro_df.index[pro_df['Product Name'] == product][0]
            pro_df.at[idx, 'Quantity'] -= quantity
    else:
        idx = pro_df.index[pro_df['Product Name'] == list_of_products][0]
        pro_df.at[idx, 'Quantity'] -= quantity_of_products

    update_product_file(pro_df)
    
def upload_order(list_of_products, quantity_of_products, sell_price):
    order_df = get_order_df()
    order_number = order_df.tail(1)['Order Number'][0]+1
    date_ = date.today()
    prof, rev = calculate_profit(
    list_of_products, quantity_of_products, sell_price)

    if len(list_of_products) > 1 and type(quantity_of_products) == list:
        ps = list_of_products[0]+' '+str(quantity_of_products[0])
    else:
        ps = list_of_products+' '+str(quantity_of_products)
    
    


    if ((len(list_of_products) > 1) and (type(quantity_of_products) == list)):
        zip_object = zip(list_of_products[1:], quantity_of_products[1:])
        for product, quantity in zip_object:
            ps += ' | ' + product + ' '+str(quantity)
    new_row = {
        'Order Number' : order_number,
        'Date of Order' : date_,
        'Revenue' : rev,
        'Profit' : prof,
        'Products': ps
        
    }
    df = order_df.append(new_row, ignore_index = True)
    update_product_table(list_of_products, quantity_of_products)
    update_order_file(df)
        



 #updated_table = update_ims_csv(units, ingredient, n_units, price)
def update_ims_csv(units_of_measurement, ingredient_name, n_units, price):
    
    df = pd.read_csv('/Users/johnwelsh/Desktop/ERBA-CRUD/inventory_master_file.csv')
    
    #First check to see if the ingredient is already in the data
    if ingredient_name in list(df.Ingredient):
        
        
        new_cpm = price/n_units
        
        if units_of_measurement == 'oz':
            # print(units_of_measurement, ingredient_name, n_units, price)
            # print(np.floor(df.loc[df.loc[df.Ingredient == ingredient_name].index, ['Current Amount (ounces)']]) *  0)

            df.loc[df.loc[df.Ingredient == ingredient_name].index, ['Current Amount (ounces)']] += n_units
            df.loc[df.loc[df.Ingredient == ingredient_name].index, ['Current Amount (grams)']] += n_units*28.3496
        else:
            df.loc[df.loc[df.Ingredient == ingredient_name].index, ['Current Amount (ounces)']] += n_units * .035274
            df.loc[df.loc[df.Ingredient == ingredient_name].index, ['Current Amount (grams)']] += n_units

        df.loc[df.loc[df.Ingredient == ingredient_name].index, ['Total Cost']] += price
        
        df.loc[df.loc[df.Ingredient == ingredient_name].index, ['Current Value']] += price
        
        df.loc[df.loc[df.Ingredient == ingredient_name].index, ['Cost Per Measurement Unit']] = new_cpm
        
        table = dbc.Table.from_dataframe(
            df, striped=True, bordered=True, hover=True
        )
        update_inventory_file(df)
        
        
        return table
    #Otherwise add a new row to the existing data frame
    else:
        if units_of_measurement == 'oz':
            new_row = {
            'Ingredient': ingredient_name,
            'Current Amount (ounces)': n_units,
            'Current Amount (grams)': n_units*28.3496,
            'Measurement Unit': units_of_measurement,
            'Total Cost': price,
            'Cost Per Measurement Unit': price/n_units,
            'Current Value': price
             }
        else:
            new_row = {
            'Ingredient': ingredient_name,
            'Current Amount (ounces)': n_units*.035274,
            'Current Amount (grams)': n_units,
            'Measurement Unit': units_of_measurement,
            'Total Cost': price,
            'Cost Per Measurement Unit': price/n_units,
            'Current Value': price
             }


        
        df = df.append(new_row, ignore_index = True)
        update_inventory_file(df)
        table = dbc.Table.from_dataframe(
            df, striped=True, bordered=True, hover=True
        )
        return table

def add_product(product_name, quantity):
    print('AT THE TOP')
    pro_df = get_product_df()
    inventory_df = get_inventory_df()
    recipe = list(recipes[product_name])
    #loop thru neccessary items and deduct from inventory
    #loop thru neccessary items and deduct from inventory
#     print('RECIPE IS')
#     print(recipe)
    for ingredient in recipe:
        #determine name, quantity, and unit of measurement
        split = ingredient.split()
        quantity_ = split[-1]
        ingredient_name = ''
        for part in split[0:-1]:
            ingredient_name += part
            ingredient_name = (ingredient_name+' ')
        ingredient_name = ingredient_name[0:-1]
        #index of ingredient
        idx = inventory_df.index[inventory_df['Ingredient'] == ingredient_name][0]
        
        #Now pull ingredient from ingredient df
        if quantity_[-1] == 'z':
            amount = float(quantity_.split('o')[0] * quantity)
#             print(amount)
#             print(idx)
#             print(ingredient_name)
            
            print(inventory_df.loc[idx].at['Current Amount (ounces)'])
            inventory_df.at[idx, 'Current Amount (ounces)'] -= amount
            inventory_df.at[idx, 'Current Amount (grams)'] = \
            inventory_df.at[idx, 'Current Amount (grams)'] - (amount*28.3495)
            #print('Made it to the end')
            
        else:
            
            amount = float(quantity_.split('g')[0] * quantity)
            inventory_df.at[idx, 'Current Amount (ounces)']  -= (amount*0.035274)
            inventory_df.at[idx, 'Current Amount (grams)'] -= amount
        
        rate = inventory_df.loc[idx].at['Cost Per Measurement Unit']
        if inventory_df.at[idx, 'Measurement Unit'] == 'oz':
            value = inventory_df.loc[idx].at['Current Amount (ounces)'] * rate
            inventory_df.at[idx, 'Current Value'] = value
        else:
            value = inventory_df.loc[idx].at['Current Amount (grams)'] * rate
            inventory_df.at[idx, 'Current Value'] = value
    #Now that we have updated the inventory table I just need to update
    #the product table
    
    idx = pro_df.index[pro_df['Product Name'] == product_name][0]
    pro_df.at[idx, 'Quantity'] += quantity
    pro_df.at[idx, 'Total Cost'] = \
        pro_df.at[idx, 'Quantity'] * pro_df.at[idx, 'Individual Cost']
    update_product_file(pro_df)  
    update_inventory_file(inventory_df)


###################################################################################################
########################################  APP ELEMENTS  ###########################################
###################################################################################################

available_ingredients = list(pd.read_csv('/Users/johnwelsh/Desktop/ERBA-CRUD/ingredient_list.csv').Ingredient)
available_products = list(pd.read_csv('/Users/johnwelsh/Desktop/ERBA-CRUD/product_list.csv').Product)
as_df = pd.DataFrame({
        'c' : available_ingredients
    })
pd_df = pd.DataFrame({
        'c' : available_products
    })


inventory_table =  get_inventory_table()
product_table = get_product_table()
order_table = get_order_table()
########################################  Main Page  ##############################################


main_row_one = html.Div(dbc.Row
    ([
        dbc.Col(html.H1(children = 'WELCOME TO THE ERBA CRUD SYSTEM', style={'text-align': 'center'}),
        align='center', 
        ), 
        dbc.Col(html.Div(
            dbc.Button(id='refresh_button', n_clicks = 0,  children = 'Refresh')

        ))
         ],class_name='g-0') 

)



main_row_two = html.Div(dbc.Row([
    html.Div([
########################################  Product TAB  ##############################################
        dcc.Tabs(id='main-tabs', value='product-tab', children = [

                    dcc.Tab(label = 'Products', value='product-tab', 
                    children = [
                        dbc.Row(
                            html.Div(dbc.Alert(
                                    "Please Enter Valid Data For The Product Info",
                                    id = 'fas-insufficient',
                                    dismissable = True,
                                    is_open = False,
                                    color = 'danger'
                                ))),
                        dbc.Row( [ 
                            dbc.Col(
                                html.Div(
                                    product_table,
                                    id = 'product_table'
                                )        
                            ),
                        dbc.Col(
                        html.Div([ 
           
 
                            html.Div([
                                dcc.Dropdown(
                                    placeholder = "Add-Product",
                                    options = [
                                    {'label':i, 'value':i} for i in pd_df['c'].unique()
                                ], value="none", id='product_dropdown')

                            ]),                             
                            html.Div([
                                    dcc.Input(id='add_product_quantity', type='number', placeholder = 'Quantity?')

                                ]),
                            
                            html.Div([
                                    dbc.Button(id='add_product', n_clicks = 0,  children = 'Submit-Product(s)')

                                ])
                    ]), width = 2

                         ),
                                           
                    ], class_name='g-0')]
                    
                    ),
########################################  ORDER TAB  ##############################################
                    dcc.Tab(label = 'Orders', value = 'order-tab', 
                    children = [ 
                    dbc.Row(
                            html.Div(dbc.Alert(
                                    "Please Enter Valid Data For The Product Info",
                                    id = 'insufficient-order',
                                    dismissable = True,
                                    is_open = False,
                                    color = 'danger'
                                ))),
                    
                    
                    
                     dbc.Row([ 
                            dbc.Col(
                                html.Div(
                                    get_order_table(), id = 'the_order_table'
                                )        
                            ),
                            dbc.Col([
                            ###############Product One#####################
                            dbc.Row([
                                dbc.Col( 
                                html.Div([
                                dcc.Dropdown(id='input_order_one', placeholder = "Add Ingredient", value = "none", options = [
                                    {'label':i, 'value':i} for i in pd_df['c'].unique()
                                ], searchable=True)

                            ])),
                            dbc.Col(
                            html.Div([
                                dcc.Input(id='add_product_quantity_one', type='number', placeholder = 'Quantity?')
                                
                            ])),
                            dbc.Col(
                                html.Div(
                                    dcc.Input(id='add_product_price_one', type='number', placeholder = 'Price?')
                                )
                            )

                            ] ),
                            ###############Product Two #####################
                            dbc.Row([
                                dbc.Col( 
                                html.Div([
                                dcc.Dropdown(id='input_order_two', placeholder = "Add Ingredient", value = "none", options = [
                                    {'label':i, 'value':i} for i in pd_df['c'].unique()
                                ], searchable=True)

                            ])),
                            dbc.Col(
                            html.Div([
                                dcc.Input(id='add_product_quantity_two', type='number', placeholder = 'Quantity?')
                                
                            ])),
                            dbc.Col(
                                html.Div(
                                    dcc.Input(id='add_product_price_two', type='number', placeholder = 'Price?')
                                )
                            )

                            ], id = 'product_two_row', style = dict(display = 'none')),
                            ###############Product Three #####################
                            dbc.Row([
                                dbc.Col( 
                                html.Div([
                                dcc.Dropdown(id='input_order_three', placeholder = "Add Ingredient", value = "none", options = [
                                    {'label':i, 'value':i} for i in pd_df['c'].unique()
                                ], searchable=True)

                            ])),
                            dbc.Col(
                            html.Div([
                                dcc.Input(id='add_product_quantity_three', type='number', placeholder = 'Quantity?')
                                
                            ])),
                            dbc.Col(
                                html.Div(
                                    dcc.Input(id='add_product_price_three', type='number', placeholder = 'Price?')
                                )
                            )

                            ], id='product_three_row', style = dict(display = 'none')),
                            ###############Product Four #####################
                            dbc.Row([
                                dbc.Col( 
                                html.Div([
                                dcc.Dropdown(id='input_order_four', placeholder = "Add Ingredient", value = "none", options = [
                                    {'label':i, 'value':i} for i in pd_df['c'].unique()
                                ], searchable=True)

                            ])),
                            dbc.Col(
                            html.Div([
                                dcc.Input(id='add_product_quantity_four', type='number', placeholder = 'Quantity?')
                                
                            ])),
                            dbc.Col(
                                html.Div(
                                    dcc.Input(id='add_product_price_four', type='number', placeholder = 'Price?')
                                )
                            )

                            ], id = 'product_four_row', style = dict(display = 'none')),
                            ###############Product Five #####################
                            dbc.Row([
                                dbc.Col( 
                                html.Div([
                                dcc.Dropdown(id='input_order_five', placeholder = "Add Ingredient", value = "none", options = [
                                    {'label':i, 'value':i} for i in pd_df['c'].unique()
                                ], searchable=True)

                            ])),
                            dbc.Col(
                            html.Div([
                                dcc.Input(id='add_product_quantity_five', type='number', placeholder = 'Quantity?')
                                
                            ])),
                            dbc.Col(
                                html.Div(
                                    dcc.Input(id='add_product_price_five', type='number', placeholder = 'Price?')
                                )
                            )

                            ], id = 'product_five_row', style = dict(display = 'none')),

                            ############# SUBMIT ORDER ######################
                            dbc.Row([ 
                                dbc.Col(
                                    html.Div([
                                        dbc.Button(id='add_order_submit', n_clicks = 0,  children = 'Submit-Order'),
                                        dbc.Button(id='additional_product_button', n_clicks = 0, children = '+'),
                                        dbc.Button(id='subtract_product_button', n_clicks = 0, children = '-')
                                        
                                        
                                        ]
                                    )
                                ),
                                # dbc.Col(
                                #     html.Div(
                                #         dbc.Button(id='additional_product_button', n_clicks = 0, children = 'Add Another')
                                #     )
                                # )
                            ], class_name='g-2')
                            ])
                            


                        

                        ]) ]
                                           
                    ),
                    ########################################  Inventory TAB  ##############################################
                    dcc.Tab(label = "Inventory", value = "inventory-tab", children = [dbc.Row
                        ([
                            dbc.Col(
                                html.Div([ 
                                dbc.Alert(
                                    "Please Enter Valid Data For The Ingredient Info",
                                    id = 'Alert',
                                    dismissable = True,
                                    is_open = False,
                                    color = 'danger'
                                ),


        
        
                                        ]),
                                        align = 'center'
                                        ),
                                        ],class_name='g-0'),
                                        
                                dbc.Row([
                                dbc.Col(
                                    html.Div([
                                        
                                        dbc.Table(
                                        id = 'inventory_table',
                                        children = inventory_table)

                                    ]), 

                                ),
                                dbc.Col(
                                    html.Div(
                                        [
                        
                                    html.Div([
                                        dcc.Dropdown(id='input_ingredient', placeholder = "Add Ingredient", value = "none", options = [
                                            {'label':i, 'value':i} for i in as_df['c'].unique()
                                        ], searchable=True,)

                                    ]), 

                                    html.Div([
                                            dcc.Dropdown(id='units_of_measurement', placeholder = "Units of Measurement", value='none', options = [
                                                    {'label' : 'Ounces', 'value': 'oz'},
                                                    {'label' : 'Grams', 'value': 'g'},
                                                
                                            ], searchable=False, clearable=False)

                                        ]),
                                    
                                    html.Div([
                                            dcc.Input(id='add_ingredient_quantity', type='number', placeholder = 'Quantity?')

                                        ]),
                                    
                                    html.Div([
                                            dcc.Input(id='add_ingredient_price', type='number', placeholder = 'Price?')

                                        ]),
                                    html.Div([
                                            dbc.Button(id='add_ingredient_sumbit', n_clicks = 0,  children = 'Submit-Ingredient')

                                        ]),
                                    
                                        ]
                                    ),

                                    width = 2

                            ),

                            
                                ],class_name='g-0')  ]

                                ),
########################################  Analytics  ###################################################
                                dcc.Tab(label = "Analytics", value = "analytics-tab", children = dbc.Row([
                                ])),
                                ]) 
                                ])
                                ]))
                                
                                 
                                                       
                                                        
###################################################################################################
########################################  APP LAYOUT  #############################################
###################################################################################################


main_children = [main_row_one, main_row_two]


app.layout = html.Div(
    id='main_div',
    children=main_children,
    style={'width': '100%', 'margin': 'auto', 'padding': '2'}
)
###################################################################################################
########################################  CALLBACKS  ##############################################
###################################################################################################

########################################  Main Page Callbacks #####################################
########################################  Order Callbacks ###########################################
# @app.callback(
    
# )


@app.callback(
    Output('product_two_row', 'style'),
    Output('product_three_row', 'style'),
    Output('product_four_row', 'style'),
    Output('product_five_row', 'style'),
    Output('additional_product_button', 'n_clicks'),
    Output('subtract_product_button', 'n_clicks'),
    
    Input('additional_product_button', 'n_clicks'),
    Input('subtract_product_button', 'n_clicks'),
    
)
def add_products(add_product, subtract_product):
    hide = dict(display = 'none')
    n = get_num_products()
    
    if (add_product > 0) and (n <= 4):
        
        n += 1
        set_num_products(n)
    elif subtract_product > 0 and n >= 2:
        
        n -= 1
        set_num_products(n)
    
    if n <= 1:
        return hide, hide, hide, hide, 0, 0
    elif n == 2:
        return dict(), hide, hide, hide, 0, 0
    elif n == 3:
        return dict(), dict(), hide, hide, 0, 0
    elif n == 4:
        return dict(), dict(), dict(), hide, 0, 0
    elif n >= 5:
        return dict(), dict(), dict(), dict(), 0, 0
    
    return dict(), dict(), dict(), dict(), 0, 0

@app.callback(
     Output('the_order_table', 'children'),
     Output('add_order_submit', 'n_clicks'),
     Output('insufficient-order', 'is_open'),

     Input('add_order_submit', 'n_clicks'),
     State('input_order_one', 'value'),
     State('add_product_quantity_one', 'value'),
     State('add_product_price_one', 'value'),
     State('input_order_two', 'value'),
     State('add_product_quantity_two', 'value'),
     State('add_product_price_two', 'value'),
     State('input_order_three', 'value'),
     State('add_product_quantity_three', 'value'),
     State('add_product_price_three', 'value'),
     State('input_order_four', 'value'),
     State('add_product_quantity_four', 'value'),
     State('add_product_price_four', 'value'),

 )         
def submit_order(submit, product_one, quantity_one, price_one, \
                         product_two, quantity_two, price_two, \
                         product_three, quantity_three, price_three, \
                         product_four, quantity_four, price_four):
    
    n = get_num_products()
    if submit > 0:
        # print('N is ')
        # print(n)
        # print('Product two is ')
        # print(product_two)
        # print('is product two none?')
        # print(product_two == 'none')
        if n <= 1:
            if product_one == 'none' or quantity_one == None  or price_one == None:
                return get_order_table(), 0, True
            else:
                upload_order(product_one, quantity_one, price_one)
                return get_order_table(), 0, False
            
        elif n == 2:
            if product_two == 'none' or quantity_two == None  or price_two == None or \
            product_one == 'none' or quantity_one == None  or price_one == None:
                return get_order_table(), 0, True
            else:
                upload_order([product_one, product_two], [quantity_one,  quantity_two], [price_one, price_two])
                return get_order_table(), 0, False
            
        elif n == 3:
            if product_two == 'none' or quantity_two == None  or price_two == None or \
            product_one == 'none' or quantity_one == None  or price_one == None or \
            product_three == 'none' or quantity_three == None  or price_three == None:
                return get_order_table(), 0, True
            else:
                upload_order([product_one, product_two, product_three], 
                [quantity_one, quantity_two, quantity_three], 
                [price_one, price_two, price_three])

                return get_order_table(), 0, False
            
        elif n == 4:
            if product_two == 'none' or quantity_two == None  or price_two == None or \
            product_one == 'none' or quantity_one == None  or price_one == None or \
            product_three == 'none' or quantity_three == None  or price_three == None or \
            product_four == 'none' or quantity_four == None  or price_four == None:
                return get_order_table(), 0, True
            else:
                upload_order([product_one, product_two, product_three, product_four], 
                [quantity_one, quantity_two, quantity_three, quantity_four], 
                [price_one, price_two, price_three, price_four])
                
                return get_order_table(), 0, False
        else:
            return get_order_table(), 0, False
            
    else:
        return get_order_table(), 0, False
        


########################################  IMS Callbacks ###########################################
@app.callback(
    Output('inventory_table', 'children'),
    Output('add_ingredient_sumbit', 'n_clicks'),
    Output('Alert', 'is_open'),

    Output('units_of_measurement', 'value'),
    Output('input_ingredient', 'value'),
    Output('add_ingredient_quantity', 'value'),
    Output('add_ingredient_price', 'value'),

    Input('add_ingredient_sumbit', 'n_clicks'),
    Input('refresh_button', 'n_clicks'),
    State('units_of_measurement', 'value'),
    State('input_ingredient', 'value'),
    State('add_ingredient_quantity', 'value'),
    State('add_ingredient_price', 'value'),
    
    
)
def add_ingredient(n_clicks, units, ingredient, n_units, price, refresh):
    if  n_clicks > 0:
        if ( (units == 'none') | (ingredient == 'none') | (n_units == None) | (price == None)):
            return get_inventory_table(), 0, True, None, None, None, None
        else:

            updated_table = update_ims_csv(units, ingredient, n_units, price)
            return updated_table, 0, False, None, None, None, None
        
    else:
        return get_inventory_table(), 0, False, None, None, None, None

# @app.callback(
#     Output('refresh_button', 'n_clicks'),
#     Input('refresh_button', 'n_clicks')
# )
# def refresh(clicks):
#     if clicks > 0:
#         return 0

########################################  Product Tab Callbacks ###########################################
@app.callback(
    Output('product_table', 'children'),
    Output('product_dropdown', 'value'), 
    Output('add_product_quantity', 'value'),
    Output('add_product', 'n_clicks'),
    Output('fas-insufficient', 'is_open'),

    Input('add_product', 'n_clicks'),
    State('add_product_quantity', 'value'),
    State('product_dropdown', 'value')
)
def add_product_callback(click, quantity, product_name):
    if click > 0:
        if ((quantity == None) | (product_name ==  None)):
            return get_product_table(), None, None, 0, True
        else:
            

            add_product(product_name, quantity)
            return get_product_table(), None, None, 0, False

    else:
        return get_product_table(), None, None, 0, False


        


###################################################################################################
########################################  SERVER  #################################################
###################################################################################################
if __name__ == '__main__':
    app.run_server(debug=True, port=8000, host='127.0.0.1')
    #port=8000, host='127.0.0.1'