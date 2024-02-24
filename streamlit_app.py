import streamlit as st
import requests

# URLs atualizadas
consultarItemMaterial_base_url = 'https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial'
consultarItemServico_base_url = 'https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/3_consultarServico'

def obter_itens(tipo_item, codigo_item_catalogo):
    url = consultarItemMaterial_base_url if tipo_item == 'Material' else consultarItemServico_base_url
    params = {
        'pagina': 1,
        'tamanhoPagina': 500,
        'codigoItemCatalogo': codigo_item_catalogo
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        json_response = response.json()
        # Diagnóstico para verificar a estrutura de um item
        if json_response.get('resultado'):
            st.write("Exemplo de item:", json_response['resultado'][0])
        
        itens = json_response.get('resultado', [])
        # Supondo que cada item na lista 'resultado' tenha as chaves corretas
        # Este código precisa ser ajustado com base na estrutura real do item
        return [(item.get('codigoItem', 'Código não disponível'), 
                 f"{item.get('descricao', 'Descrição não disponível')} (código: {item.get('codigoItem', 'n/a')})") for item in itens]
    else:
        st.error(f"Erro na consulta: {response.status_code}")
        return []

# Streamlit UI
st.title("Consulta de Itens de Material e Serviço")

tipo_item = st.selectbox("Selecione o tipo de item para consulta", ['Material', 'Serviço'], key='tipo_item')
codigo_item_catalogo = st.text_input("Código do Item de Catálogo", value="267666", key='codigo_item_catalogo')

if st.button('Consultar', key='btn_consultar'):
    itens = obter_itens(tipo_item, codigo_item_catalogo)
    if itens:
        for codigo, descricao in itens:
            st.write(descricao)
    else:
        st.error("Nenhum item encontrado ou erro na consulta.")
