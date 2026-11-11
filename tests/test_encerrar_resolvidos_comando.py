"""O comando manual apenas dispara a API uma vez e não expõe a credencial."""

from unittest.mock import Mock

import pytest
import requests

from scripts.encerrar_resolvidos import CONTAGENS, verificar_encerramento


def resposta_valida():
    return dict.fromkeys(CONTAGENS, 0) | {"avaliados": 3, "encerrados": 1}


def test_dispara_uma_unica_requisicao_sem_enviar_ids():
    cliente = Mock()
    cliente.post.return_value.json.return_value = resposta_valida()

    resultado = verificar_encerramento("https://xano.example/api:servicedesk/", "chave", 10, cliente)

    assert resultado["encerrados"] == 1
    cliente.post.assert_called_once_with(
        "https://xano.example/api:servicedesk/automacao/encerrar-resolvidos",
        headers={"X-MIRA-Encerramento-Key": "chave"},
        timeout=10,
    )


def test_falha_de_rede_nao_tenta_novamente():
    cliente = Mock()
    cliente.post.side_effect = requests.Timeout()

    with pytest.raises(requests.Timeout):
        verificar_encerramento("https://xano.example/api:servicedesk", "chave", 10, cliente)

    assert cliente.post.call_count == 1


@pytest.mark.parametrize("dados", [{}, [], {"avaliados": True}, {"avaliados": -1}])
def test_resposta_invalida_e_recusada(dados):
    cliente = Mock()
    cliente.post.return_value.json.return_value = dados

    with pytest.raises(ValueError, match="Resposta de encerramento inválida"):
        verificar_encerramento("https://xano.example/api:servicedesk", "chave", 10, cliente)
