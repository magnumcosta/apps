import streamlit as st
import requests
import pandas as pd

# URLs atualizadas
consultarItemMaterial_base_url = 'https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial'
consultarItemServico_base_url = 'https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/3_consultarServico'

def obter_itens(tipo_item, codigo_item_catalogo=''):
    url = consultarItemMaterial_base_url if tipo_item == 'Material' else consultarItemServico_base_url
    params = {
        'pagina': 1,
        'tamanhoPagina': 500
    }
    if codigo_item_catalogo:
        params['codigoItemCatalogo'] = codigo_item_catalogo

    response = requests.get(url, params=params)
    if response.status_code == 200:
        json_response = response.json()
        itens = json_response.get('resultado', [])
        return [(item['codigoItem'], f"{item.get('descricao', 'Descrição não disponível')} (código: {item['codigoItem']})") for item in itens]
    else:
        return []

# Streamlit UI
st.title("Consulta de Itens de Material e Serviço")

tipo_item = st.selectbox("Selecione o tipo de item para consulta", ['Material', 'Serviço'], key='tipo_item')
codigo_item_catalogo = st.text_input("Código do Item de Catálogo (opcional)", key='codigo_item_catalogo')

if st.button('Consultar', key='btn_consultar'):
    itens = obter_itens(tipo_item, codigo_item_catalogo)
    if itens:
        for codigo, descricao in itens:
            st.write(descricao)
    else:
        st.error("Nenhum item encontrado ou erro na consulta.")

