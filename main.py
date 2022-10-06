import streamlit as st
import pandas as pd
import altair as alt
from streamlit_option_menu import option_menu

# ---------------------------------pandas---------------------------------

data=pd.read_csv('data.csv')  #reading financial data

#separating expenses and income
expenses_data=data[ (data['Amount']<0) & (~data['category'].isin(['misc']))]  #removing miscellaneous amounts
expenses_data=expenses_data.drop(['Number','Account','Subcategory', 'Memo'], axis=1)
expenses_data['Amount']=expenses_data['Amount']*-1
income_data = data[data['Amount']>0]


#TOTAL INCOME
all_income=income_data['Amount']
total_income=all_income.sum()


#TOTAL EXPENSES
all_expenses=expenses_data['Amount']
total_expenses=all_expenses.sum()


#NET INCOME
net_income=total_income-total_expenses



#GRAPH

#Categories
ent=expenses_data.loc[expenses_data['category'] == 'entertainment', 'Amount']
uni=expenses_data.loc[expenses_data['category'] == 'uni', 'Amount']
car=expenses_data.loc[expenses_data['category'] == 'car', 'Amount']
food=expenses_data.loc[expenses_data['category'] == 'food', 'Amount']
travel=expenses_data.loc[expenses_data['category'] == 'travel', 'Amount']
health=expenses_data.loc[expenses_data['category'] == 'health', 'Amount']
shopping=expenses_data.loc[expenses_data['category'] == 'shopping', 'Amount']
charity=expenses_data.loc[expenses_data['category'] == 'charity', 'Amount']


newData={
    'Amount':[ent.sum(), uni.sum(), round(car.sum(),2), food.sum(), travel.sum(),
              health.sum(), shopping.sum(), charity.sum()],
    'Category': ['entertainment', 'uni', 'car', 'food', 'travel',
                 'health', 'shopping', 'charity']
}

dfCat=pd.DataFrame(newData)
print(dfCat)

#RECENT EXPENSES TABLE
tb1 = expenses_data.loc[0:10, ['Date', 'Amount', 'category']]


#-----------------------------------Streamlit--------------------------------------
header = st.container()
if 'totalExpenses' not in st.session_state or 'netIncome' not in st.session_state or 'totalIncome' not in st.session_state:
    st.session_state.totalExpenses = total_expenses
    st.session_state.netIncome = net_income
    st.session_state.totalIncome = net_income



if 'tableDf' not in st.session_state or 'chart' not in st.session_state:
    st.session_state.tableDf = tb1
    st.session_state.chart= dfCat

with header:
    st.title('Your Monthly Expense Tracker!')





def handleSubmit(type):
    if type== 'Expense':
        st.session_state.totalExpenses = st.session_state.totalExpenses + new_amount
        st.session_state.netIncome = st.session_state.netIncome - new_amount
    elif type== 'Income':
        st.session_state.totalIncome = st.session_state.totalIncome + new_amount

    col1, col2, col3 = st.columns(3)

    col1.caption('Net Income')
    col1.subheader(round(st.session_state.netIncome, 2))

    col2.caption('Total Income')
    col2.subheader(round(st.session_state.totalIncome, 2))

    col3.caption('Total Expenses')
    col3.subheader(round(st.session_state.totalExpenses, 2))

    #Updating graph state
    prevVal=st.session_state.chart.loc[st.session_state.chart['Category']==new_cat, 'Amount']
    st.session_state.chart.loc[st.session_state.chart['Category']==new_cat,'Amount']=prevVal+new_amount

    c = alt.Chart(st.session_state.chart).mark_bar().encode(

        y='Amount',
        x='Category'
    )


    #updating table state
    newTableDf = pd.DataFrame({
        'Date': [new_date],
        'Amount': [new_amount],
        'category': [new_cat]
    })
    st.session_state.tableDf=pd.concat([newTableDf, st.session_state.tableDf], ignore_index=True)

    # CSS to inject contained in a string
    hide_table_row_index = """
                <style>
                thead tr th:first-child {display:none}
                tbody th {display:none}
                </style>
                """

    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)

    #removing rows with 0 amount:
    st.session_state.tableDf=st.session_state.tableDf[st.session_state.tableDf['Amount']!=0]

    #DISPLAYING GRAPH/TABLE
    graphCol, tableCol = st.columns(2)

    #GRAPH
    graphCol.subheader('Spending Categories')
    graphCol.altair_chart(c, use_container_width=True)

    #TABLE
    tableCol.subheader('Recent Activities')
    tableCol.table(st.session_state.tableDf)



#CREATING OPTION MENU
selected = option_menu(
    menu_title=None,
    options=['Expenses', 'Income' ],
    orientation='horizontal'
)

if selected == 'Expenses':
    type='Expense'
    form = st.form('Add New Expense')
    form.header('Add New Expense')
    new_date = form.date_input('What date did you make the expense?', on_change=None, value=None)
    new_amount = form.number_input('How much was the expense')
    new_cat = form.selectbox(
        'Please select the category',
        ('car', 'charity', 'entertainment', 'food', 'health', 'shopping', 'travel', 'uni'))

    Submit=form.form_submit_button('Submit', on_click=handleSubmit('Expense'))

elif selected == 'Income':
    type='Income'
    form = st.form('Add Income')
    form.header('Add Income')
    new_date = form.date_input('What date did you receive the income?', on_change=None, value=None)
    new_amount = form.number_input('How much did you get?')
    new_cat = form.selectbox(
        'Please select the category',
        ('Salary', 'other'))
    Submit = form.form_submit_button('Submit', on_click=handleSubmit('Income'))


