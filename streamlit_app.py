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
        json_response = response.json()
        itens = json_response.get('resultado', [])
        return itens, json_response.get('totalRegistros', 0)
    else:
        st.error(f"Erro na consulta: {response.status_code}")
        return [], 0

# Streamlit UI
st.title("Consulta de Itens de Material e Serviço")

# Disclaimer
st.markdown("""
**Disclaimer:** tetetetetettetettttsssssssssssssssss
""")

tipo_item = st.selectbox("Selecione o tipo de item para consulta", ['Material', 'Serviço'], key='tipo_item')
codigo_item_catalogo = st.text_input("Código do Item de Catálogo", value="", key='codigo_item_catalogo')
pagina = st.number_input("Indique a página para consulta", min_value=1, value=1, step=1)

if st.button('Consultar'):
    st.session_state['itens'], st.session_state['total_registros'] = obter_itens(tipo_item, codigo_item_catalogo, pagina)

if st.session_state.get('itens'):
    st.write(f"Total de registros encontrados: {st.session_state['total_registros']}")
    # Mostrar os itens em formato de tabela
    tabela_itens = [{
        "Código": item.get('codigoItemCatalogo', 'Código não disponível'), 
        "Descrição": item.get('descricaoItem', 'Descrição não disponível'), 
        "Preço Unit.": formatar_preco_reais(item.get('precoUnitario')),
        "Data do resultado": item.get('dataResultado')
    } for item in st.session_state['itens']]
    df = pd.DataFrame(tabela_itens)
    st.table(df)

    # Opção para download dos dados
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download dos dados em CSV",
        data=csv,
        file_name='dados_consulta.csv',
        mime='text/csv',
    )
