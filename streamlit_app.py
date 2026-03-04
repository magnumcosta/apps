import streamlit as st
import requests
import pandas as pd

CONSULTAR_MATERIAL_URL = 'https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial'
CONSULTAR_SERVICO_URL  = 'https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/3_consultarServico'

REQUEST_TIMEOUT = 30  # segundos


def formatar_preco_reais(valor):
    """Formata um float como preço no padrão brasileiro (ex: 1.234,56)."""
    if valor is None:
        return 'Preço não disponível'
    return f'{valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def float_para_csv(valor):
    """Converte float para string decimal BR (vírgula, sem ponto de milhar).
    Mantém o valor reconhecível como número pelo Excel pt-BR."""
    if isinstance(valor, float):
        return f'{valor:.2f}'.replace('.', ',')
    return valor


# Mapeamento de nomes de colunas da API → rótulos legíveis em português
RENOMEAR_COLUNAS = {
    'idCompra':                    'ID Compra',
    'idItemCompra':                'ID Item',
    'forma':                       'Forma',
    'modalidade':                  'Modalidade',
    'criterioJulgamento':          'Critério Julgamento',
    'numeroItemCompra':            'Nº Item',
    'descricaoItem':               'Descrição do Item',
    'codigoItemCatalogo':          'Cód. Catálogo',
    'nomeUnidadeMedida':           'Unidade Medida',
    'siglaUnidadeMedida':          'Sigla Unidade Medida',
    'nomeUnidadeFornecimento':     'Unidade Fornecimento',
    'siglaUnidadeFornecimento':    'Sigla Unid. Fornecimento',
    'capacidadeUnidadeFornecimento': 'Capacidade Unid. Fornecimento',
    'quantidade':                  'Quantidade',
    'precoUnitario':               'Preço Unitário (R$)',
    'percentualMaiorDesconto':     'Desconto (%)',
    'niFornecedor':                'CNPJ/CPF Fornecedor',
    'nomeFornecedor':              'Fornecedor',
    'marca':                       'Marca',
    'codigoUasg':                  'Cód. UASG',
    'nomeUasg':                    'UASG',
    'codigoMunicipio':             'Cód. Município',
    'municipio':                   'Município',
    'estado':                      'UF',
    'codigoOrgao':                 'Cód. Órgão',
    'nomeOrgao':                   'Órgão',
    'poder':                       'Poder',
    'esfera':                      'Esfera',
    'dataCompra':                  'Data da Compra',
    'dataHoraAtualizacaoCompra':   'Atualização Compra',
    'dataHoraAtualizacaoItem':     'Atualização Item',
    'dataResultado':               'Data Resultado',
    'dataHoraAtualizacaoUasg':     'Atualização UASG',
    'codigoClasse':                'Cód. Classe',
    'nomeClasse':                  'Classe',
    'objetoCompra':                'Objeto da Compra',
    'descricaoDetalhadaItem':      'Descrição Detalhada',
}


def obter_itens(tipo_item, codigo_item_catalogo, pagina, tamanho_pagina):
    """Consulta a API do Compras.gov.br e retorna os itens encontrados."""
    url = CONSULTAR_MATERIAL_URL if tipo_item == 'Material' else CONSULTAR_SERVICO_URL
    params = {
        'pagina': pagina,
        'tamanhoPagina': tamanho_pagina,
        'codigoItemCatalogo': codigo_item_catalogo
    }
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        json_response = response.json()
        itens = json_response.get('resultado', [])
        paginas_restantes = json_response.get('paginasRestantes', 0)
        total_paginas = json_response.get('totalPaginas', 0)
        return itens, paginas_restantes, total_paginas
    except requests.exceptions.Timeout:
        st.error("A requisição excedeu o tempo limite. Tente novamente.")
        return [], 0, 0
    except requests.exceptions.HTTPError as e:
        st.error(f"Erro HTTP na consulta: {e}")
        return [], 0, 0
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao realizar a requisição: {e}")
        return [], 0, 0

# =============================================================================
# Interface
# =============================================================================
st.title("Pesquisa de Preços de Materiais e/ou Serviços")
st.markdown(
    "Localize o código do material ou serviço no "
    "[Catálogo de Compras](https://catalogo.compras.gov.br/cnbs-web/busca) "
    "antes de consultar."
)

st.divider()

col1, col2 = st.columns(2)
with col1:
    tipo_item = st.selectbox("Tipo de item", ['Material', 'Serviço'], key='tipo_item')
    codigo_item_catalogo = st.text_input("Código do Item de Catálogo", value="", key='codigo_item_catalogo')
with col2:
    pagina = st.number_input("Página", min_value=1, value=1, step=1)
    tamanho_pagina = st.number_input("Itens por página", min_value=10, value=500, step=10)

if st.button('Consultar', type='primary'):
    # Limpa resultado anterior a cada nova consulta
    st.session_state.pop('itens', None)
    st.session_state.pop('paginas_restantes', None)
    st.session_state.pop('total_paginas', None)

    if not codigo_item_catalogo.strip():
        st.warning("Por favor, informe o código do item de catálogo para realizar a consulta.")
    else:
        with st.spinner('Consultando a API do Compras.gov.br...'):
            itens, paginas_restantes, total_paginas = obter_itens(
                tipo_item, codigo_item_catalogo.strip(), pagina, tamanho_pagina
            )
        if itens:
            st.session_state['itens'] = itens
            st.session_state['paginas_restantes'] = paginas_restantes
            st.session_state['total_paginas'] = total_paginas
        else:
            st.error("Nenhum item encontrado. Verifique o código informado ou tente novamente.")

# Exibe resultados e botão de download fora do bloco do botão,
# para que persistam entre reruns do Streamlit.
if st.session_state.get('itens'):
    try:
        itens = st.session_state['itens']
        if isinstance(itens, list) and all(isinstance(item, dict) for item in itens):
            df_completo = pd.json_normalize(itens)

            # DataFrame de exibição: formata preços com ponto de milhar e vírgula decimal
            df_exibicao = df_completo.map(
                lambda x: formatar_preco_reais(x) if isinstance(x, float) else x
            )
            df_exibicao = df_exibicao.rename(columns=RENOMEAR_COLUNAS)

            # DataFrame de exportação: números com vírgula decimal, sem ponto de milhar
            # Encoding utf-8-sig (BOM) garante leitura correta no Excel do Windows
            df_csv = df_completo.map(float_para_csv)
            df_csv = df_csv.rename(columns=RENOMEAR_COLUNAS)

            st.success(
                f"Total de páginas: {st.session_state['total_paginas']} | "
                f"Páginas restantes: {st.session_state['paginas_restantes']}"
            )
            st.dataframe(df_exibicao, width='stretch')

            csv = df_csv.to_csv(sep=';', index=False).encode('utf-8-sig')
            st.download_button(
                label="Download dos dados em CSV",
                data=csv,
                file_name='dados_consulta.csv',
                mime='text/csv',
                type='secondary',
            )
        else:
            st.error("Formato dos itens inválido para normalização.")
    except Exception as e:
        st.error(f"Erro ao processar os itens: {e}")
