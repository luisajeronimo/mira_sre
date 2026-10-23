from dataclasses import replace

from app.chamados.shared import _tecnico_para_dict, evento_timeline_para_dict
from app.services.service_desk import (
    ChamadoResumo,
    EventoTimelineChamado,
    ReferenciaAtivo,
    ReferenciaCategoria,
    ReferenciaUsuario,
)


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
    assert resultado["alteracoes_detalhadas"] == [
        {
            "campo": "Responsável",
            "anterior": "Técnico #Camila Santos",
            "resultante": "Técnico #Beatriz Souza",
        }
    ]


def test_resumo_tecnico_expoe_ultima_atualizacao_formatada():
    chamado = ChamadoResumo(
        id=40,
        titulo="Falha de rede",
        descricao="Sem conexão",
        status="Novo",
        prioridade="Alta",
        origem="manual",
        criado_em=1_790_000_000_000,
        ultima_atualizacao_em=1_790_000_060_000,
        sla_horas_aplicado=2,
        atribuido_em=None,
        ativo=ReferenciaAtivo(id=1, nome_ativo="Totem 1"),
        categoria=ReferenciaCategoria(id=1, nome="Rede"),
        solicitante=ReferenciaUsuario(id=1, nome="Gerente"),
        tecnico=None,
    )

    visual = _tecnico_para_dict(chamado)

    assert visual["ultima_atualizacao_em_texto"] != "Não informado"
    assert visual["ultima_atualizacao_em_texto"] != visual["criado_em_texto"]
    assert visual["aberto_por"] == "Gerente"
    assert _tecnico_para_dict(
        replace(chamado, origem="automatico", solicitante=None, criador_sistema="bot_fiscalizacao")
    )["aberto_por"] == "Bot de Fiscalização"
    assert _tecnico_para_dict(replace(chamado, solicitante=None))["aberto_por"] == "Não informado"
