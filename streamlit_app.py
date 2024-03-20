import streamlit as st
import requests
import locale

# Tente configurar o locale para pt_BR
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    try:
        # Tenta um fallback para outra variação comum se a primeira falhar
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except locale.Error:
        st.error("Locale pt_BR não pôde ser configurado.")


# URLs atualizadas
consultarItemMaterial_base_url = 'https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial'
consultarItemServico_base_url = 'https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/3_consultarServico'

def obter_itens(tipo_item, codigo_item_catalogo, pagina):
    url = consultarItemMaterial_base_url if tipo_item == 'Material' else consultarItemServico_base_url
    params = {
        'pagina': pagina,
        'tamanhoPagina': 10,  # Modificado para 10 registros por página
        'codigoItemCatalogo': codigo_item_catalogo
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        json_response = response.json()
        itens = json_response.get('resultado', [])
        return itens, json_response.get('totalRegistros', 0)  # Retornar também o total de registros
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
    st.session_state['pagina_atual'] = 1  # Resetar a paginação ao fazer uma nova consulta

pagina_atual = st.session_state['pagina_atual']
itens, total_registros = obter_itens(tipo_item, codigo_item_catalogo, pagina_atual)

if itens:
    # Mostrar os itens em formato de tabela
    tabela_itens = [{
        "Código": item.get('codigoItemCatalogo', 'Código não disponível'), 
        "Descrição": item.get('descricaoItem', 'Descrição não disponível'), 
        "Preço Unit.": item.get('precoUnitario', 'Preço não disponível'), 
        "Preço Unit.": locale.currency(item.get('precoUnitario', 0), grouping=True) if item.get('precoUnitario') else 'Preço não disponível',
        "Data do resultado": item.get('dataResultado', 'Data não disponível')
    } for item in itens]
    st.table(tabela_itens)
    
    # Paginação
    if st.button('Anterior', key='btn_anterior'):
        if st.session_state['pagina_atual'] > 1:
            st.session_state['pagina_atual'] -= 1
    if st.button('Próximo', key='btn_proximo'):
        if pagina_atual * 10 < total_registros:
            st.session_state['pagina_atual'] += 1
else:
    st.error("Nenhum item encontrado ou erro na consulta.")
