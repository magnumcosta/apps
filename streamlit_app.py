import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Função para formatar preço em reais
def formatar_preco_reais(valor):
    if valor is None:
        return 'Preço não disponível'
    else:
        return f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

# URLs atualizadas
consultarItemMaterial_base_url = 'https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial'
consultarItemServico_base_url = 'https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/3_consultarServico'

def obter_itens(tipo_item, codigo_item_catalogo, pagina):
    url = consultarItemMaterial_base_url if tipo_item == 'Material' else consultarItemServico_base_url
    params = {
        'pagina': pagina,
        'tamanhoPagina': 10,
        'codigoItemCatalogo': codigo_item_catalogo
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        json_response = response.json()
        itens = json_response.get('resultado', [])
        return itens, json_response.get('totalRegistros', 0)
    else:
        st.error(f"Erro na consulta: {response.status_code}")
        return [], 0

# Inicialização das variáveis de sessão para controle da paginação
if 'pagina_atual' not in st.session_state:
    st.session_state['pagina_atual'] = 1

# Streamlit UI
st.title("Consulta de Itens de Material e Serviço")

tipo_item = st.selectbox("Selecione o tipo de item para consulta", ['Material', 'Serviço'], key='tipo_item')
codigo_item_catalogo = st.text_input("Código do Item de Catálogo", value="267666", key='codigo_item_catalogo')

if st.button('Consultar', key='btn_consultar'):
    st.session_state['pagina_atual'] = 1

pagina_atual = st.session_state['pagina_atual']
itens, total_registros = obter_itens(tipo_item, codigo_item_catalogo, pagina_atual)

if itens:
    st.write(f"Total de registros encontrados: {total_registros}")

    # Processamento para gráfico
    data = []
    for item in itens:
        preco = item.get('precoUnitario')
        data_resultado = item.get('dataResultado', '1900-01-01')
        mes_ano = datetime.strptime(data_resultado, "%Y-%m-%d").strftime("%m/%Y")
        data.append({"Mes/Ano": mes_ano, "Preço": preco})

    df = pd.DataFrame(data)
    df['Preço'] = pd.to_numeric(df['Preço'], errors='coerce')
    agrupado = df.groupby('Mes/Ano').agg(Total_Registros=('Mes/Ano', 'count'), Media_Precos=('Preço', 'mean')).reset_index()

    # Plot
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    agrupado.plot(kind='bar', x='Mes/Ano', y='Total_Registros', ax=ax1, position=0, color='skyblue', figsize=(10, 6))
    agrupado.plot(kind='line', x='Mes/Ano', y='Media_Precos', ax=ax2, color='darkred', marker='o')
    ax1.set_ylabel('Total de

