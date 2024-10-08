import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from api import bank
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from supabaseDB import Supabase

#@TODO:
# - update graphs
# - more sub transaction types
# - allow user to create sub transaction types
# - update records with sub transaction types

supabase = Supabase()
st.set_page_config(page_title="Bank", page_icon="💰")

if 'file_id' not in st.session_state:
    st.session_state.file_id = 0

@st.cache_data
def get_bank_records():
    records = supabase.getBankRecords()
    if records is False:
        return False

    df = pd.DataFrame()
    for record in records:
        row = pd.DataFrame([record])
        df = pd.concat([df,row], ignore_index=True)

    return df

@st.cache_data
def get_bank_budget_presets():
    return bank.getBudgetPresets()

@st.cache_data
def get_transaction_types():
    transaction_types_dict = bank.getTransactionTypes()
    if transaction_types_dict is False:
        return False, False
    else:
        transaction_types_list = [i for i in transaction_types_dict['Transaction Types'].keys()]
        return transaction_types_dict, transaction_types_list

def statementImport(df:pd.DataFrame, transaction_types:dict):
    for index, row in df.iterrows():
        try:
            date = row['Date']
            date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
            name = str(row['Name'])
            amount = round(float(row['Amount']),2)

            if amount < 0:
                _type = 0
            else:
                _type = 1

            amount = abs(amount)
            transaction = "Unknown"

            for key in transaction_types['Transaction Types'].keys():
                for i in key:
                    if i.upper() in name.upper():
                        transaction = key
                        break

        except Exception as e:
            print(e)
            continue

        try:
            duplicate = supabase.getBankRecordsDuplicate({"name":name,"amount":amount,"date":date})
            print(f"Duplicate: {duplicate}")

            if duplicate:
                print(f"Duplicate Record Name: {name}, Amount: {amount}, Date: {date}")
                continue

            else:
                print(f"Inserting Bank Record Name: {name}, Amount: {amount}, Date: {date}, Type: {_type} Transaction: {transaction}")

                supabase.insertBankRecord(
                    name=name,
                    amount=amount,
                    date=date,
                    _type=_type,
                    transaction=transaction,
                    categories=""
                )

        except Exception as e:
            print(e)
            continue

    st.cache_data.clear()

def statementImportButton(disabled:bool):
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv",disabled=disabled, key=st.session_state.file_id)
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        if df.empty:
            st.warning("File is empty")
            return False
        else:
            return df

    else:
        return False

def recordForm(df:pd.DataFrame, transaction_types:list, transaction_types_dict:dict, edit_id=None):

    # Get Editid record
    if edit_id != None:
        record = df.loc[df['id'] == edit_id]
        name = record['name'].values[0]
        amount = record['amount'].values[0]
        date = datetime.strptime(record['date'].values[0], "%Y-%m-%d")
        _type = record['type'].values[0]
        title="Edit"
        delete_button = False

    else:
        name = ""
        amount = 0.00
        date = datetime.today()
        _type = "Income"
        title="Insert"
        delete_button = True

    # Form
    with st.form("Record"):
        st.subheader(title)
        name = st.text_input("Name",value=name)
        amount = st.number_input("Amount",value=amount, min_value=0.00, format="%.2f")
        date = st.date_input("Date", value=date)
        _type = st.selectbox(
            "Transaction Types",
            options=transaction_types,
            index=transaction_types.index(_type) if _type in transaction_types else 0
        )
        submitted = st.form_submit_button(label="Submit")

    delete = st.button(label="Delete",
        key="delete",
        disabled=delete_button,
        use_container_width=True
    )

    statement_df = statementImportButton(disabled= not delete_button)
    if statement_df is False:
        pass
    else:
        with st.spinner("Importing Statement..."):
            statementImport(df=statement_df,
                transaction_types=transaction_types_dict)
        st.session_state.file_id += 1

    if submitted:
        if not name:
            st.warning("Name is required")

        elif edit_id is None:
            response = supabase.insertBankRecord(
                name=name,
                amount=round(amount,2),
                date=date.strftime("%Y-%m-%d"),
                _type=_type,
                categories=""
            )
            if response is False:
                st.warning("Failed to insert record")
            else:
                st.cache_data.clear()
                st.success("Record inserted")

        else:
            response = supabase.updateBankRecord(
                id=edit_id,
                name=name,
                amount=amount,
                date=date.strftime("%Y-%m-%d"),
                _type=_type,
                categories=""
            )
            if response is False:
                st.warning("Failed to update record")
            else:
                st.cache_data.clear()
                st.success("Record updated")

    elif delete and edit_id is not None:
        response = supabase.deleteBankRecord(id=edit_id)
        if response:
            st.warning("Failed to delete record")
        else:
            st.cache_data.clear()
            st.success("Record deleted")

def recordTable(df:pd.DataFrame):
    # Filter
    if df.empty:
        st.warning("No records found")
        return None

    unique_types = df['type'].unique().tolist()
    unique_types.insert(0, "All")
    selected_type = st.selectbox("Filter by Type", options=unique_types)

    if selected_type != "All":
        df = df[df['type'] == selected_type]

    # Configure
    df = df.sort_values(by='id', ascending=False)
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
    if df.empty:
        st.warning("No records found")
        return

    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%B')
    df['year'] = df['date'].dt.year
    df['month'] = pd.Categorical(df['month'], categories=[
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'], ordered=True)

    # Filter
    years = df['year'].unique()
    selected_year = st.selectbox("Select Year", options=sorted(years, reverse=True))
    filtered_df_year = df[df['year'] == selected_year]

    color_discrete_map = {
        "Income": "green",
        "Expense": "yellow",
        "Bill": "red"
    }

    income_avg = filtered_df_year[filtered_df_year['type'] == 'Income']['amount'].mean()
    expense_avg = filtered_df_year[filtered_df_year['type'] == 'Expense']['amount'].mean()
    bill_avg = filtered_df_year[filtered_df_year['type'] == 'Bill']['amount'].mean()
    other_avg = filtered_df_year[filtered_df_year['type'] == 'Other']['amount'].mean()

    # Bar Chart
    fig = px.bar(
        filtered_df_year,
        x='month',
        y='amount',
        color='type',  # Grouping by 'type'
        barmode='group',  # Grouped bars
        title="Monthly Amounts by Type",
        labels={'amount': 'Amount', 'month': 'Month'},
        category_orders={'month': ['January', 'February', 'March', 'April', 'May', 'June',
                                'July', 'August', 'September', 'October', 'November', 'December']},
        color_discrete_map=None
    )
    # Add average lines
    fig.add_trace(go.Scatter(
        x=filtered_df_year['month'].unique(),
        y=[income_avg] * len(filtered_df_year['month'].unique()),
        mode='lines',
        name='Income Avg',
        line=dict(color='green', dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=filtered_df_year['month'].unique(),
        y=[expense_avg] * len(filtered_df_year['month'].unique()),
        mode='lines',
        name='Expense Avg',
        line=dict(color='yellow', dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=filtered_df_year['month'].unique(),
        y=[bill_avg] * len(filtered_df_year['month'].unique()),
        mode='lines',
        name='Bill Avg',
        line=dict(color='red', dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=filtered_df_year['month'].unique(),
        y=[other_avg] * len(filtered_df_year['month'].unique()),
        mode='lines',
        name='Other Avg',
        line=dict(color='blue', dash='dash')
    ))

    st.title("Monthly Amounts by Type")
    st.plotly_chart(fig)

    # Month Filter
    filtered_df_year['month'] = filtered_df_year['date'].dt.strftime('%B')
    filtered_df_year['month'] = pd.Categorical(filtered_df_year['month'], categories=[
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'], ordered=True)

    selected_month = st.selectbox("Select Month", options=filtered_df_year['month'].unique())
    filtered_df_month = filtered_df_year[filtered_df_year['month'] == selected_month]

    # Calculate Metrics
    metrics = ["Income", "Expense", "Bill", "Other"]
    red_metrics = ["Expense", "Bill", "Other"]
    columns = st.columns(len(metrics))
    for i, metric in enumerate(metrics):
        # Calulate Percentage Change
        year_average_amount = filtered_df_year[filtered_df_year['type'] == metric]['amount'].mean()
        current_amount = filtered_df_month[filtered_df_month['type'] == metric]['amount'].sum()
        percentage_change = round(((current_amount - year_average_amount) / year_average_amount) * 100, 2)

        # Display Metrics
        columns[i].metric(label=metric, value=current_amount, delta=f"{percentage_change}%",
                          delta_color="inverse" if metric in red_metrics else "normal",
                          help=f"Yearly Average: {year_average_amount}")

    # Total Income for Month
    total_income = filtered_df_month[filtered_df_month['type'] == 'Income']['amount'].sum()

    # Total Type amount for Month
    expense_total = filtered_df_month[filtered_df_month['type'] == 'Expense']['amount'].sum()
    bill_total = filtered_df_month[filtered_df_month['type'] == 'Bill']['amount'].sum()
    other_total = filtered_df_month[filtered_df_month['type'] == 'Other']['amount'].sum()

    # Free Money Left
    free_amount = total_income - (expense_total + bill_total + other_total)

    # Pie Chart Data
    pie_data = pd.DataFrame({
        'type': ['Expense', 'Bill', 'Other', 'Free'],
        'amount': [expense_total, bill_total, other_total, free_amount]
    })

    fig_pie = px.pie(
        pie_data,
        names='type',
        values='amount',
        title=f"Total Income: ${total_income}",
        color_discrete_map=color_discrete_map
    )

    st.title(f"Monthly Breakdown - {selected_month} {selected_year}")
    st.plotly_chart(fig_pie)

def recordsMetrics(df:pd.DataFrame):
    pass

def budgetBreakdown():
    presets = get_bank_budget_presets()
    if presets is False:
        st.warning("Error, Unable to load Presets")
        return False

    total = st.number_input("Expected Monthly Income", value=0.0, min_value=0.0)

    if total > 0.0:
        preset_options = presets.keys()
        selected_preset = st.selectbox("Select Budget", options=preset_options)

    else:
        return

    # Values
    essentials = total * round(presets[selected_preset]['essentials'] / 100,2)
    savings = total * round(presets[selected_preset]['savings'] / 100,2)
    spending = total * round(presets[selected_preset]['spending'] / 100,2)
    # Pie Chart
    fig_pie = px.pie(
        names=['Essentials', 'Savings', 'Spending'],
        values=[essentials, savings, spending],
        title=f"{presets[selected_preset]['essentials']}% Essentials, {presets[selected_preset]['savings']}% Savings, {presets[selected_preset]['spending']}% Spending",
        color_discrete_map=None
    )

    st.plotly_chart(fig_pie)

def bankView():
    transaction_types_dict, transaction_types_list = get_transaction_types()
    if transaction_types_dict is False or transaction_types_list is False:
        st.error("Failed to get Transaction Types")
        return False

    df = get_bank_records()
    if df is False:
        st.error("Failed to get Bank records")
        return False

    tab1, tab2, tab3 = st.tabs(tabs=["Records","Graph", "Budget"])

    # Table
    with tab1:
        id = recordTable(df)
        if id is None:
            recordForm(df=df,
                transaction_types=transaction_types_list,
                transaction_types_dict=transaction_types_dict
            )
        else:
            recordForm(df=df,
                transaction_types=transaction_types_list,
                transaction_types_dict=transaction_types_dict,
                edit_id=id
            )

    # Graph
    with tab2:
        recordGraphs(df)

    # Budget
    with tab3:
        budgetBreakdown()

bankView()
