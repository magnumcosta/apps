import streamlit as st
import requests
import pandas as pd

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
        'tamanhoPagina': 500,  # Ajuste para 500 itens por página
        'codigoItemCatalogo': codigo_item_catalogo
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()  # Retorna a resposta completa
    else:
        st.error(f"Erro na consulta: {response.status_code}")
        return {"resultado": [], "paginasRestantes": 0}

# Streamlit UI (mantenha como está, até a parte da consulta)

# Quando preparar o DataFrame para download:
if st.session_state.get('itens'):
    # Supondo que `st.session_state['itens']` agora tenha a resposta completa
    json_response = st.session_state['itens']
    itens = json_response.get('resultado', [])

    # Adaptação para usar todos os campos disponíveis
    df_completo = pd.json_normalize(itens)  # Isto transformará todos os campos em colunas
    df_completo = df_completo.applymap(lambda x: formatar_preco_reais(x) if isinstance(x, float) else x)  # Formatando preços

    csv = df_completo.to_csv(sep=';', index=False).encode('utf-8')
    st.download_button(
        label="Download dos dados em CSV",
        data=csv,
        file_name='dados_consulta.csv',
        mime='text/csv',
    )

