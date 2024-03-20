import streamlit as st
import requests
from collections import defaultdict
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

# Streamlit UI
st.title("Consulta de Itens de Material e Serviço")

tipo_item = st.selectbox("Selecione o tipo de item para consulta", ['Material', 'Serviço'])
codigo_item_catalogo = st.text_input("Código do Item de Catálogo", value="267666")

if st.button('Consultar'):
    itens, total_registros = obter_itens(tipo_item, codigo_item_catalogo, 1)
    if itens:
        st.write(f"Total de registros encontrados: {total_registros}")
        
        # Processamento dos dados para cálculo da média de preços por mês/ano
        precos_por_mes = defaultdict(list)
        for item in itens:
            data = item.get('dataResultado', '1900-01-01')
            preco = item.get('precoUnitario', 0)
            mes_ano = datetime.strptime(data, "%Y-%m-%d").strftime("%m/%Y")
            precos_por_mes[mes_ano].append(float(preco))
        
        # Exibição dos dados processados
        for mes_ano, precos in precos_por_mes.items():
            media_preco = sum(precos) / len(precos)
            st.write(f"{mes_ano}: Média de Preços = {formatar_preco_reais(media_preco)}, Total de Registros = {len(precos)}")
    else:
        st.error("Nenhum item encontrado ou erro na consulta.")



