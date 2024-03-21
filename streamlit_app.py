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
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            json_response = response.json()
            itens = json_response.get('resultado', [])
            paginas_restantes = json_response.get('paginasRestantes', 0)
            return itens, paginas_restantes
        else:
            st.error(f"Erro na consulta: {response.status_code}")
            return [], 0
    except Exception as e:
        st.error(f"Erro ao realizar a requisição: {str(e)}")
        return [], 0

# Streamlit UI
st.title("Consulta de Itens de Material e Serviço")

# Disclaimer
st.markdown("**Disclaimer:** Informações fornecidas como estão sem garantias.")

tipo_item = st.selectbox("Selecione o tipo de item para consulta", ['Material', 'Serviço'], key='tipo_item')
codigo_item_catalogo = st.text_input("Código do Item de Catálogo", value="", key='codigo_item_catalogo')
pagina = st.number_input("Indique a página para consulta", min_value=1, value=1, step=1)

if st.button('Consultar'):
    if codigo_item_catalogo:  # Verifica se o código do item de catálogo não está vazio
        itens, paginas_restantes = obter_itens(tipo_item, codigo_item_catalogo, pagina)
        if itens:  # Ensure 'itens' is not empty before proceeding
            st.session_state['itens'] = itens
            st.session_state['paginas_restantes'] = paginas_restantes
            st.write(f"Páginas restantes: {paginas_restantes}")
        else:
            st.error("Nenhum item encontrado. Por favor, tente com um código diferente ou verifique a conexão com a API.")
    else:
        st.warning("Por favor, informe o código do item de catálogo para realizar a consulta.")

if st.session_state.get('itens'):
    try:
        # Ensure 'itens' is in the expected format before normalization
        if isinstance(st.session_state['itens'], list) and all(isinstance(item, dict) for item in st.session_state['itens']):
            df_completo = pd.json_normalize(st.session_state['itens'])
            # Apply formatting
            df_completo = df_completo.applymap(lambda x: formatar_preco_reais(x) if isinstance(x, float) else x)
            
            csv = df_completo.to_csv(sep=';', index=False)
            st.download_button(
                label="Download dos dados em CSV",
                data=csv,
                file_name='dados_consulta.csv',
                mime='text/csv',
            )
        else:
            st.error("Formato dos itens inválido para normalização.")
    except Exception as e:
        st.error(f"Erro ao processar os itens: {str(e)}")
