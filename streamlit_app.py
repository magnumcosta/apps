import streamlit as st
import requests

consultaGrupoMaterial_base_url = 'https://dadosabertos.compras.gov.br/modulo-material/1_consultarGrupoMaterial?pagina='

def consultar_grupo_material(pagina, codigo_grupo=None):
    # Construindo a URL base com o número da página
    consultaGrupoMaterial_url = f"{consultaGrupoMaterial_base_url}{pagina}"
    
    # Adicionando o parâmetro opcional codigoGrupo, se fornecido
    if codigo_grupo is not None:
        consultaGrupoMaterial_url += f"&codigoGrupo={codigo_grupo}"
    
    # Fazendo a requisição GET com o parâmetro opcional, se aplicável
    response = requests.get(consultaGrupoMaterial_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Criando inputs no Streamlit para número da página e código do grupo
pagina = st.number_input("Digite o número da página", min_value=1, value=1, step=1)
codigo_grupo = st.text_input("Digite o código do grupo (opcional)", "")

# Chamando a função com o número da página e o código do grupo (se fornecido)
dados = consultar_grupo_material(pagina, codigo_grupo if codigo_grupo != "" else None)

# Exibindo os dados ou uma mensagem de erro
if dados:
    st.write(dados)
else:
    st.error("Erro ao acessar o endpoint")
