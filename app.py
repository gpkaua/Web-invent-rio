import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import init_db, add_product, get_all_products, update_stock, get_financial_report

# Page config
st.set_page_config(page_title="Gestão de Estoque", layout="wide")

# Initialize DB
init_db()

st.title("📦 Sistema de Gestão de Estoque")

# Sidebar Navigation
menu = ["Cadastro de Produtos", "Entrada/Saída de Estoque", "Dashboard Financeiro"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Cadastro de Produtos":
    st.header("🆕 Cadastro de Novo Produto")

    with st.form("product_form"):
        name = st.text_input("Nome do Produto")
        cost_price = st.number_input("Preço de Custo (R$)", min_value=0.0, format="%.2f")

        # Logic: Auto-calculate sale price with 35% margin
        default_sale_price = cost_price * 1.35
        sale_price = st.number_input("Preço de Venda (R$)", min_value=0.0, value=default_sale_price, format="%.2f")

        submit = st.form_submit_button("Cadastrar Produto")

        if submit:
            if name and cost_price > 0:
                add_product(name, cost_price, sale_price)
                st.success(f"Produto {name} cadastrado com sucesso!")
            else:
                st.error("Por favor, preencha todos os campos corretamente.")

    st.divider()
    st.subheader("Produtos Cadastrados")
    products = get_all_products()
    if products:
        df_products = pd.DataFrame([dict(p) for p in products])
        st.dataframe(df_products, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado.")

elif choice == "Entrada/Saída de Estoque":
    st.header("🔄 Movimentação de Estoque")

    products = get_all_products()
    if not products:
        st.warning("Cadastre produtos primeiro para realizar movimentações.")
    else:
        product_list = {p['name']: p['id'] for p in products}

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Entrada de Estoque")
            with st.form("entry_form"):
                prod_in = st.selectbox("Produto (Entrada)", options=list(product_list.keys()), key="in")
                qty_in = st.number_input("Quantidade", min_value=1, step=1)
                submit_in = st.form_submit_button("Registrar Entrada")
                if submit_in:
                    update_stock(product_list[prod_in], qty_in, 'IN')
                    st.success(f"Entrada de {qty_in} unidades de {prod_in} registrada!")

        with col2:
            st.subheader("Saída de Estoque")
            with st.form("exit_form"):
                prod_out = st.selectbox("Produto (Saída)", options=list(product_list.keys()), key="out")
                qty_out = st.number_input("Quantidade", min_value=1, step=1)
                submit_out = st.form_submit_button("Registrar Saída")
                if submit_out:
                    update_stock(product_list[prod_out], qty_out, 'OUT')
                    st.success(f"Saída de {qty_out} unidades de {prod_out} registrada!")

elif choice == "Dashboard Financeiro":
    st.header("📊 Dashboard Financeiro")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Data Inicial", value=date(2023, 1, 1))
    with col2:
        end_date = st.date_input("Data Final", value=date.today())

    report_data = get_financial_report(start_date, end_date)

    if report_data:
        df_report = pd.DataFrame([dict(r) for r in report_data], columns=['name', 'qty_sold', 'total_revenue'])
        df_report.columns = ['Produto', 'Qtd Vendida', 'Total Vendido (R$)']

        st.dataframe(df_report, use_container_width=True)

        total_geral = df_report['Total Vendido (R$)'].sum()
        st.metric("Total Geral do Período", f"R$ {total_geral:,.2f}")
    else:
        st.info("Não há vendas registradas para o período selecionado.")
