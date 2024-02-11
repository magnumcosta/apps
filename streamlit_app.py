import streamlit as st
import requests

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

# Streamlit UI
st.title("Consulta de Grupos de Material")

# Obter grupos para seleção
grupos = obter_grupos()
grupo_selecionado = st.selectbox("Selecione o grupo para consulta", grupos, format_func=lambda x: x[1], key='grupo_selecionado')

# Incluindo um botão de consulta
if st.button('Consultar', key='btn_consultar'):
    if grupo_selecionado:
        codigo_grupo, nome_grupo = grupo_selecionado
        dados_grupo = consultar_grupo_material(1, codigo_grupo)  # Consulta inicial para obter o total de páginas
        if dados_grupo:
            total_paginas = dados_grupo.get('totalPaginas', 1)
            st.write(f"Total de páginas para {nome_grupo.split(' (código:')[0]}: {total_paginas}")
            
            # Usando a key para garantir um identificador único para o widget
            pagina_key = f"pagina_{codigo_grupo}"
            pagina = st.number_input("Escolha a página", min_value=1, max_value=total_paginas, value=1, key=pagina_key)
            
            # Consultar dados da página selecionada
            dados_pagina = consultar_grupo_material(pagina, codigo_grupo)
            if dados_pagina:
                st.json(dados_pagina)
            else:
                st.error("Erro ao obter dados da página selecionada.")
        else:
            st.error("Erro ao acessar detalhes do grupo.")
