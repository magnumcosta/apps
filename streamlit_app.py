import streamlit as st
import requests
import pandas as pd

# URLs atualizadas
consultarItemMaterial_base_url = 'https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial'
consultarItemServico_base_url = 'https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/3_consultarServico'

def obter_itens(tipo_item, codigo_item_catalogo=''):
    if tipo_item == 'Material':
        response = requests.get(f"{consultarItemMaterial_base_url}?pagina=1&tamanhoPagina=500&codigoItemCatalogo={codigo_item_catalogo}")
    elif tipo_item == 'Serviço':
        response = requests.get(f"{consultarItemServico_base_url}?pagina=1&codigoItemCatalogo={codigo_item_catalogo}")
    else:
        return []

    if response.status_code == 200:
        itens = response.json().get('resultado', [])
        return [(item['codigoItem'], f"{item['descricao']} (código: {item['codigoItem']})") for item in itens]
    else:
        return []

# Streamlit UI
st.title("Consulta de Itens de Material e Serviço")

tipo_item = st.selectbox("Selecione o tipo de item para consulta", ['Material', 'Serviço'], key='tipo_item')

codigo_item_catalogo = st.text_input("Código do Item de Catálogo (opcional)", key='codigo_item_catalogo')

if st.button('Consultar', key='btn_consultar'):
    itens = obter_itens(tipo_item, codigo_item_catalogo)
    if itens:
        for item in itens:
            st.write(item[1])
    else:
        st.error("Nenhum item encontrado ou erro na consulta.")

