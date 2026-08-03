# Fix: quebra na consulta de Materiais (API Dados Abertos Compras.gov.br)

Status: **concluído** — fix implementado, testado (TDD) e validado contra a API real

## 1. Problema

A consulta de **Materiais** no app passou a falhar com erro HTTP 404, reportado
com dois códigos de catálogo diferentes (mesmo padrão de erro nos dois casos):

```
Erro HTTP na consulta: 404 Client Error: Resource Not Found for url:
https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial?pagina=1&tamanhoPagina=500&codigoItemCatalogo=618302
```

```
Erro HTTP na consulta: 404 Client Error: Resource Not Found for url:
https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial?pagina=1&tamanhoPagina=500&codigoItemCatalogo=606524
```

A consulta de **Serviços** (`3_consultarServico`) não apresenta o mesmo erro.

## 2. Causa raiz

Investigação sistemática (Phase 1–2 de debugging: reprodução, checagem da
documentação oficial da API via OpenAPI/Swagger, comparação de contrato)
identificou que o **provedor da API (Compras.gov.br) alterou o contrato de
parâmetros do endpoint `1_consultarMaterial`**, sem alterar o endpoint de
Serviço.

Fonte oficial consultada: `GET https://dadosabertos.compras.gov.br/v3/api-docs`
(Swagger/OpenAPI v3 exposto publicamente pelo provedor).

| Endpoint | Parâmetro de busca **antigo** (usado no código) | Parâmetro de busca **atual** (exigido pela API) |
|---|---|---|
| `1_consultarMaterial` | `codigoItemCatalogo` (string) | `tipo` (enum: `codigoItemCatalogo` \| `codigoPdm`, obrigatório) + `codigo` (obrigatório) |
| `3_consultarServico` | `codigoItemCatalogo` (string) | **inalterado** — continua `codigoItemCatalogo` (obrigatório) |

O parâmetro `codigoItemCatalogo`, hoje **obrigatório e não reconhecido** pelo
endpoint de Material sem o par `tipo`/`codigo`, faz o roteador da API
(Spring/Springdoc) não casar a requisição a nenhuma operação válida — daí o
404 genérico (`Resource not found`), em vez de um 400 mais explícito.

O **schema de resposta não mudou**: todos os campos usados no código
(`RENOMEAR_COLUNAS` em `streamlit_app.py`) continuam presentes e com os
mesmos nomes no DTO `FtPesqPrecoCompraMaterialDTO` da API. O problema está
apenas na **query de entrada**, não no parsing da resposta.

### Evidência de reprodução (antes do fix)

```bash
$ curl -s -w "\nHTTP:%{http_code}\n" \
  "https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial?pagina=1&tamanhoPagina=500&codigoItemCatalogo=618302"
{ "statusCode": 404, "message": "Resource not found" }
HTTP:404

$ curl -s -w "\nHTTP:%{http_code}\n" \
  "https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial?pagina=1&tamanhoPagina=500&codigoItemCatalogo=606524"
{ "statusCode": 404, "message": "Resource not found" }
HTTP:404
```

### Evidência de que o novo contrato funciona (confirmação da causa raiz)

```bash
$ curl -s -w "\nHTTP:%{http_code}\n" \
  "https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial?pagina=1&tamanhoPagina=500&tipo=codigoItemCatalogo&codigo=618302"
HTTP:200   # 1091 registros retornados

$ curl -s -w "\nHTTP:%{http_code}\n" \
  "https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial?pagina=1&tamanhoPagina=500&tipo=codigoItemCatalogo&codigo=606524"
HTTP:200   # totalRegistros: 406, itens: 406
```

### Achado secundário (fora da causa raiz, mas relacionado)

O endpoint (ambos, Material e Serviço) valida `tamanhoPagina` no intervalo
**10–500**. Fora desse intervalo, a API responde `400` com a mensagem
`"Informe um número de paginação no intervalo de 10 a 500"`. O componente de
UI (`st.number_input` de "Itens por página") define `min_value=10` mas **não
define `max_value`**, permitindo ao usuário digitar valores acima de 500 e
receber um erro evitável.

## 3. Solução proposta

Escopo: **apenas o endpoint de Material**. O endpoint de Serviço não muda
(seu contrato não foi alterado pelo provedor).

1. Extrair uma função pura `montar_params(tipo_item, codigo_item_catalogo, pagina, tamanho_pagina)`
   em `streamlit_app.py`, responsável só por montar o dicionário de query params
   conforme o contrato de cada endpoint:
   - `Material` → `{'tipo': 'codigoItemCatalogo', 'codigo': ..., 'pagina': ..., 'tamanhoPagina': ...}`
   - `Serviço` → `{'codigoItemCatalogo': ..., 'pagina': ..., 'tamanhoPagina': ...}` (mantém como está)
2. `obter_itens()` passa a usar `montar_params()` em vez de montar o dict inline.
3. Adicionar `max_value=500` ao `st.number_input` de "Itens por página" na UI,
   alinhando com o limite documentado pela API (corrige o achado secundário).
4. Cobertura via TDD: testes unitários para `montar_params()` (Material e
   Serviço), sem dependência de rede.

## 4. O que foi feito

1. Adicionada a função pura `montar_params()` em `streamlit_app.py`, extraída
   de dentro de `obter_itens()`, encapsulando a diferença de contrato entre
   Material e Serviço.
2. `obter_itens()` passou a usar `montar_params()` para montar a query.
3. Corrigido o achado secundário: `st.number_input` de "Itens por página"
   agora tem `max_value=500`, alinhado ao limite documentado pela API
   (antes só tinha `min_value=10`, sem limite superior).
4. Criado `test_streamlit_app.py` com testes unitários (TDD, sem dependência
   de rede) para `montar_params()`.
5. Adicionado `requirements-dev.txt` com `pytest` (dependência de
   desenvolvimento, não entra no ambiente de produção do Streamlit Cloud).

Nenhuma mudança no endpoint de Serviço, no parsing da resposta
(`RENOMEAR_COLUNAS`, `resultado`/`totalPaginas`/`paginasRestantes`) ou no
tratamento de exceções — escopo estritamente limitado à causa raiz
identificada.

## 5. Evidências de solução

### 5.1 TDD — RED (teste falha antes da implementação)

```
$ venv/bin/python -m pytest test_streamlit_app.py -v
ImportError while importing test module 'test_streamlit_app.py'.
E   ImportError: cannot import name 'montar_params' from 'streamlit_app'
```

### 5.2 TDD — GREEN (teste passa após implementar `montar_params`)

```
$ venv/bin/python -m pytest test_streamlit_app.py -v
test_streamlit_app.py::test_montar_params_material_usa_tipo_e_codigo PASSED
test_streamlit_app.py::test_montar_params_servico_mantem_codigo_item_catalogo PASSED
============================== 2 passed in 0.56s ===============================
```

### 5.3 Validação end-to-end contra a API real (pós-fix)

Execução usando a própria função `montar_params()` do código corrigido,
chamando os dois endpoints com os códigos de catálogo relatados no bug
(`618302` e `606524`), mais uma chamada de Serviço para confirmar ausência
de regressão:

```
Material   codigo=618302   status=200 totalRegistros=1091
  url=https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial?pagina=1&tamanhoPagina=500&tipo=codigoItemCatalogo&codigo=618302

Material   codigo=606524   status=200 totalRegistros=406
  url=https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial?pagina=1&tamanhoPagina=500&tipo=codigoItemCatalogo&codigo=606524

Serviço    codigo=618302   status=200 totalRegistros=0
  url=https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/3_consultarServico?pagina=1&tamanhoPagina=500&codigoItemCatalogo=618302
```

**Antes do fix**, as mesmas duas chamadas de Material retornavam 404 (ver
seção 2). **Depois do fix**, ambas retornam 200 OK com dados reais — o erro
relatado pelo usuário (`404 ... codigoItemCatalogo=618302` e
`codigoItemCatalogo=606524`) está resolvido.

### 5.4 Resultado da suíte completa de testes

```
$ venv/bin/python -m pytest test_streamlit_app.py -v
============================= test session starts ==============================
collected 2 items

test_streamlit_app.py::test_montar_params_material_usa_tipo_e_codigo PASSED [ 50%]
test_streamlit_app.py::test_montar_params_servico_mantem_codigo_item_catalogo PASSED [100%]

============================== 2 passed in 0.56s ===============================
```

## 6. Arquivos alterados

- `streamlit_app.py` — nova função `montar_params()`, uso em `obter_itens()`,
  `max_value=500` no `st.number_input` de itens por página
- `test_streamlit_app.py` — **novo**, testes unitários de `montar_params()`
- `requirements-dev.txt` — **novo**, dependência de teste (`pytest`)
- `docs/CHANGELOG-API-FIX.md` — este documento

## 7. Riscos e pendências

- Não há cobertura automatizada de `obter_itens()` fim a fim (a chamada
  HTTP real), já que isso exigiria mock de rede — os testes unitários cobrem
  a lógica pura de `montar_params()` e a validação end-to-end foi feita
  manualmente contra a API real (seção 5.3). Se o provedor mudar o contrato
  de resposta (não apenas de request), isso não seria pego por teste
  automatizado.
- A API do provedor pode voltar a mudar de contrato no futuro sem aviso
  formal (já ocorreu 2x: fev/2024 e a mudança atual). Não há monitoramento
  automatizado desse tipo de quebra.

## 8. Confirmação final

Fix validado em uso real na aplicação (Streamlit) para os códigos de
catálogo `618302` e `606524` — consulta de Materiais funcionando
normalmente, sem o erro 404 relatado originalmente. Consulta de Serviços
continua funcionando sem alterações.
