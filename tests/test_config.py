import reflex as rx

from rxconfig import config


def test_state_manager_nao_persiste_sessao_em_disco():
    assert config.state_manager_mode is rx.constants.StateManagerMode.MEMORY
