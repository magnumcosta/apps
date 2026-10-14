from streamlit_app import montar_params


def test_montar_params_material_usa_tipo_e_codigo():
    params = montar_params('Material', '618302', 1, 500)
    assert params == {
        'pagina': 1,
        'tamanhoPagina': 500,
        'tipo': 'codigoItemCatalogo',
        'codigo': '618302',
    }


def test_montar_params_servico_mantem_codigo_item_catalogo():
    params = montar_params('Serviço', '618302', 1, 500)
    assert params == {
        'pagina': 1,
        'tamanhoPagina': 500,
        'codigoItemCatalogo': '618302',
    }
