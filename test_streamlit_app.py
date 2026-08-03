from streamlit_app import montar_params


def test_montar_params_material_usa_tipo_e_codigo():
    """A API de Material exige o par tipo/codigo (contrato atual do provedor).
    Regressão do bug: 404 Resource Not Found ao usar codigoItemCatalogo diretamente.
    """
    params = montar_params(
        tipo_item='Material',
        codigo_item_catalogo='618302',
        pagina=1,
        tamanho_pagina=500,
    )

    assert params == {
        'pagina': 1,
        'tamanhoPagina': 500,
        'tipo': 'codigoItemCatalogo',
        'codigo': '618302',
    }
    assert 'codigoItemCatalogo' not in params


def test_montar_params_servico_mantem_codigo_item_catalogo():
    """A API de Serviço não mudou de contrato: continua usando codigoItemCatalogo."""
    params = montar_params(
        tipo_item='Serviço',
        codigo_item_catalogo='618302',
        pagina=1,
        tamanho_pagina=500,
    )

    assert params == {
        'pagina': 1,
        'tamanhoPagina': 500,
        'codigoItemCatalogo': '618302',
    }
    assert 'tipo' not in params
    assert 'codigo' not in params
