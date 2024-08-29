import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from api import bank
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def bankView():

    df = pd.DataFrame()
    records = bank.getRecords()
    for record in records:
        row = pd.DataFrame([record])
        df = pd.concat([df,row], ignore_index=True)

    tab1, tab2 = st.tabs(tabs=["Records","Graph"])

    # Table
    with tab1:
        id = recordTable(df)
        if id is None:
            recordForm(df)
        else:
            recordForm(df,edit_id=id)

    # Graph
    with tab2:
        recordGraphs(df)

def recordForm(df:pd.DataFrame, edit_id=None):

    # Get Editid record
    if edit_id != None:
        record = df.loc[df['id'] == edit_id]
        name = record['name'].values[0]
        amount = record['amount'].values[0]
        date = datetime.strptime(record['date'].values[0], "%Y-%m-%d")
        _type = record['type'].values[0]
        categories = record['categories'].values[0]
        if len(categories) == 0: categories = []
        title="Edit"
        delete_button = False

    else:
        name = ""
        amount = 0.00
        date = datetime.today()
        _type = "Income"
        categories = []
        title="Insert"
        delete_button = True

    # Form
    with st.form("Record"):
        st.subheader(title)
        name = st.text_input("Name",value=name)
        amount = st.number_input("Amount",value=amount, min_value=0.00, format="%.2f")
        date = st.date_input("Date", value=date)
        _type = st.selectbox(
            "Type", 
            options=["Income", "Bill", "Expense", "Other"],
            index=["Income", "Bill", "Expense", "Other"].index(_type) if _type in ["Income", "Bill", "Expense", "Other"] else 0
        )
        categories = st.multiselect(
            "Categories",
            options=["Test"],
            default=categories
        )
        submitted = st.form_submit_button("Submit")
        delete = st.form_submit_button("Delete",disabled=delete_button)

        if submitted and edit_id is None:
            bank.insertRecord(
                name=name,
                amount=amount,
                date=date.strftime("%Y-%m-%d"),
                _type=_type,
                categories=",".join(categories)
            )
        elif submitted:
            bank.updateRecord(
                id=edit_id,
                name=name,
                amount=amount,
                date=date.strftime("%Y-%m-%d"),
                _type=_type,
                categories=",".join(categories)
            )
        elif delete:
            bank.deleteRecord(id=edit_id)

def recordTable(df:pd.DataFrame):
    # Configure
    df = df.sort_values(by='id', ascending=True)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(selection_mode='single', use_checkbox=True)
    grid_options = gb.build()
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        enable_enterprise_modules=False,
        height=300,
        width='100%',
    )

    # Return Selected Row ID
    selected = grid_response['selected_rows']
    if isinstance(selected,pd.DataFrame):
        return selected['id'].values[0]
    else:
        return None

def recordGraphs(df:pd.DataFrame):
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%B')
    df['year'] = df['date'].dt.year
    df['month'] = pd.Categorical(df['month'], categories=[
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'], ordered=True)
    
    # Filter
    years = df['year'].unique()
    selected_year = st.selectbox("Select Year", options=sorted(years, reverse=True))
    filtered_df = df[df['year'] == selected_year]

    color_discrete_map = {
        "Income": "green",
        "Expense": "yellow",
        "Bill": "red"
    }

    fig = px.bar(
        filtered_df,
        x='month',
        y='amount',
        color='type',  # Grouping by 'type'
        barmode='group',  # Grouped bars
        title="Monthly Amounts by Type",
        labels={'amount': 'Amount', 'month': 'Month'},
        category_orders={'month': ['January', 'February', 'March', 'April', 'May', 'June',
                                'July', 'August', 'September', 'October', 'November', 'December']},
        color_discrete_map=color_discrete_map
    )

    st.title("Monthly Amounts by Type")
    st.plotly_chart(fig)