# Pesquisa de Preços - Compras.gov.br

Aplicação web desenvolvida em Streamlit para auxiliar na obtenção dos dados de pesquisa de preços do portal Compras.gov.br.

## Sobre

Esta ferramenta facilita a consulta e exportação de dados de preços de materiais e serviços registrados no sistema de compras governamentais, permitindo análises e comparações de forma simples e rápida.

## Funcionalidades

- Consulta de preços de materiais e serviços por código do catálogo
- Paginação de resultados
- Exportação dos dados em formato CSV
- Interface intuitiva e responsiva

## Como executar localmente

### 1. Criar ambiente virtual
```bash
python3 -m venv venv
```

### 2. Ativar ambiente virtual
```bash
source venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Executar aplicação
```bash
streamlit run apps/streamlit_app.py
```

### 5. Desativar ambiente virtual (quando terminar)
```bash
deactivate
```

## Acesso

A aplicação abrirá automaticamente no navegador em: http://localhost:8501

## Como usar

1. Localize o código do material ou serviço em: https://catalogo.compras.gov.br/cnbs-web/busca
2. Selecione o tipo de item (Material ou Serviço)
3. Informe o código do item de catálogo
4. Configure a página e tamanho da página desejados
5. Clique em "Consultar"
6. Faça o download dos dados em CSV

## Tecnologias

- Python 3
- Streamlit
- Pandas
- Requests

## Fonte de Dados

API de Dados Abertos do Compras.gov.br

## Equipe

**Coordenação de Transparência e Informações Gerenciais - COTIN**

**Coordenador:**
- Magnum Costa de Oliveira

**Equipe:**
- Guilherme Fonseca De Noronha Rocha
- Stefano Terci Gasperazzo
- José Maria De Melo Junior
- Páblio de Sousa Lourenço
- Flavio Henrique Martins
