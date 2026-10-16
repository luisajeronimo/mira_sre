from app.chamados.shared import evento_timeline_para_dict
from app.services.service_desk import EventoTimelineChamado, ReferenciaUsuario


def test_evento_estruturado_e_projetado_para_timeline():
    evento = EventoTimelineChamado(
        id=40,
        tipo="alteracao_chamado",
        conteudo=None,
        visibilidade="interna",
        criado_em=1792105331969,
        autor=ReferenciaUsuario(id=9, nome="Camila Santos"),
        tecnico_anterior=None,
        tecnico_novo=None,
        alteracoes={
            "responsavel": {
                "anterior": "Camila Santos",
                "resultante": "Beatriz Souza",
            }
        },
    )

    resultado = evento_timeline_para_dict(evento)

    assert resultado["titulo"] == "Alteração do chamado"
    assert resultado["alteracoes"] == evento.alteracoes
