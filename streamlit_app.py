import streamlit as st
import requests
import pandas as pd

consultaGrupoMaterial_base_url = 'https://dadosabertos.compras.gov.br/modulo-material/1_consultarGrupoMaterial'

def obter_grupos():
    response = requests.get(f"{consultaGrupoMaterial_base_url}?pagina=1")
    if response.status_code == 200:
        grupos = response.json().get('resultado', [])
        return [(grupo['codigoGrupo'], f"{grupo['nomeGrupo']} (código: {grupo['codigoGrupo']})") for grupo in grupos]
    else:
        return []

def consultar_grupo_material(pagina, codigo_grupo):
    params = {
        'pagina': pagina,
    }
    if codigo_grupo:
        params['codigoGrupo'] = codigo_grupo
    
    response = requests.get(consultaGrupoMaterial_base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def converter_para_csv(dados):
    if dados and 'resultado' in dados:
        df = pd.DataFrame(dados['resultado'])
        return df.to_csv(sep=';', index=False)
    else:
        return "Nenhum dado para exportar"

# Streamlit UI
st.title("Consulta de Grupos de Material")

grupos = obter_grupos()
grupo_selecionado = st.selectbox("Selecione o grupo para consulta", grupos, format_func=lambda x: x[1], key='grupo_selecionado')

if st.button('Consultar', key='btn_consultar'):
    if grupo_selecionado:
        codigo_grupo, nome_grupo = grupo_selecionado
        # Usando a key para garantir um identificador único para o widget
        pagina_key = f"pagina_{codigo_grupo}"
        pagina = st.number_input("Escolha a página para download", min_value=1, value=1, key=pagina_key)
        
        dados_pagina = consultar_grupo_material(pagina, codigo_grupo)
        if dados_pagina:
            csv_data = converter_para_csv(dados_pagina)
            st.download_button(
                label="Download dos dados em CSV",
                data=csv_data,
                file_name=f"dados_grupo_{codigo_grupo}_pagina_{pagina}.csv",
                mime='text/csv',
            )
        else:
            st.error("Erro ao obter dados da página selecionada.")
else:
    st.info("Selecione um grupo e clique em 'Consultar' para prosseguir.")

