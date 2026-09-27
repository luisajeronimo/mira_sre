"""Harness isolado da sequência atual de verificar-falhas.

Este arquivo não chama o Xano. O fluxo abaixo espelha a ordem do endpoint
real usando somente estruturas em memória, para regressão lógica sem alterar
ativos, telemetrias ou chamados remotos.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest


HEARTBEAT_XS = Path(__file__).parents[1] / "xano/api/apis_from_table_telemetria_equipamentos/verificar_falhas_GET.xs"


@dataclass
class FakeAsset:
    id: int
    status_atual: str


@dataclass
class FakeTelemetry:
    ativos_referencia_id: int
    evento_timestamp: int


@dataclass
class FakeCategory:
    id: int
    sla_horas: Any


@dataclass
class FakeCall:
    ativos_referencia_id: int
    categorias_servico_id: int
    status: str
    prioridade: str
    origem: str | None = None
    criado_em: int | None = None
    sla_horas_aplicado: Any = None


@dataclass
class FakeHeartbeatDb:
    assets: list[FakeAsset]
    telemetry: list[FakeTelemetry] = field(default_factory=list)
    category: FakeCategory | None = field(
        default_factory=lambda: FakeCategory(id=1, sla_horas=1)
    )
    calls: list[FakeCall] = field(default_factory=list)
    edits: list[tuple[int, str]] = field(default_factory=list)
    added: list[FakeCall] = field(default_factory=list)

    def get_heartbeat_category(self) -> FakeCategory | None:
        return self.category

    def latest_telemetry(self, asset_id: int) -> FakeTelemetry | None:
        candidates = [
            item
            for item in self.telemetry
            if item.ativos_referencia_id == asset_id
        ]
        return max(candidates, key=lambda item: item.evento_timestamp, default=None)

    def open_equivalent(self, asset_id: int, category_id: int) -> FakeCall | None:
        statuses = {"Novo", "Em Atendimento", "Aguardando Terceiro"}
        return next(
            (
                call
                for call in self.calls + self.added
                if call.ativos_referencia_id == asset_id
                and call.categorias_servico_id == category_id
                and call.status in statuses
            ),
            None,
        )

    def edit_status(self, asset: FakeAsset, status: str) -> None:
        asset.status_atual = status
        self.edits.append((asset.id, status))

    def add_call(self, call: FakeCall) -> None:
        self.added.append(call)


def executar_verificacao_isolada(
    db: FakeHeartbeatDb,
    *,
    agora: int,
    criado_em: int = 9_000,
) -> dict[str, int | bool]:
    """Espelha a ordem do endpoint sem introduzir regra nova."""

    categoria = db.get_heartbeat_category()
    limite = agora - 900_000
    online = offline = sem_telemetria = incidentes = 0

    for asset in db.assets:
        ultima = db.latest_telemetry(asset.id)
        if ultima is None:
            sem_telemetria += 1
        elif ultima.evento_timestamp < limite:
            db.edit_status(asset, "offline")
            offline += 1
            # O endpoint atual acessa a categoria somente neste ramo; não há
            # fallback de categoria nem SLA padrão.
            if categoria is None:
                raise LookupError("categoria heartbeat ausente")
            if db.open_equivalent(asset.id, categoria.id) is None:
                db.add_call(
                    FakeCall(
                        ativos_referencia_id=asset.id,
                        categorias_servico_id=categoria.id,
                        status="Novo",
                        prioridade="Urgente",
                        origem="automatico",
                        criado_em=criado_em,
                        sla_horas_aplicado=categoria.sla_horas,
                    )
                )
                incidentes += 1
        else:
            db.edit_status(asset, "online")
            online += 1

    return {
        "online": online,
        "offline": offline,
        "sem_telemetria": sem_telemetria,
        "incidentes_criados": incidentes,
    }


def test_telemetria_recente_mantem_ou_retorna_online():
    db = FakeHeartbeatDb(
        assets=[FakeAsset(id=1, status_atual="offline")],
        telemetry=[FakeTelemetry(1, 1_000_000)],
    )

    executar_verificacao_isolada(db, agora=1_899_999)

    assert db.assets[0].status_atual == "online"
    assert db.added == []


def test_telemetria_antiga_marca_offline_e_cria_incidente_com_snapshot():
    db = FakeHeartbeatDb(
        assets=[FakeAsset(id=1, status_atual="online")],
        telemetry=[FakeTelemetry(1, 99_999)],
        category=FakeCategory(id=1, sla_horas=2),
    )

    resultado = executar_verificacao_isolada(db, agora=1_000_000, criado_em=123_456)

    assert db.assets[0].status_atual == "offline"
    assert resultado["incidentes_criados"] == 1
    assert db.added == [
        FakeCall(
            ativos_referencia_id=1,
            categorias_servico_id=1,
            status="Novo",
            prioridade="Urgente",
            origem="automatico",
            criado_em=123_456,
            sla_horas_aplicado=2,
        )
    ]


def test_ativo_sem_telemetria_preserva_status_e_nao_cria_incidente():
    db = FakeHeartbeatDb(assets=[FakeAsset(id=1, status_atual="offline")])

    resultado = executar_verificacao_isolada(db, agora=1_000_000)

    assert resultado == {
        "online": 0,
        "offline": 0,
        "sem_telemetria": 1,
        "incidentes_criados": 0,
    }
    assert db.assets[0].status_atual == "offline"
    assert db.edits == []
    assert db.added == []


def test_incidente_equivalente_aberto_impede_duplicidade_sequencial():
    db = FakeHeartbeatDb(
        assets=[FakeAsset(id=1, status_atual="online")],
        telemetry=[FakeTelemetry(1, 99_999)],
    )

    primeira = executar_verificacao_isolada(db, agora=1_000_000, criado_em=1)
    segunda = executar_verificacao_isolada(db, agora=1_000_000, criado_em=2)

    assert primeira["incidentes_criados"] == 1
    assert segunda["incidentes_criados"] == 0
    assert len(db.added) == 1


def test_telemetria_recente_nao_fecha_chamado_existente():
    call = FakeCall(1, 1, "Novo", "Urgente", "automatico", 100, 2)
    db = FakeHeartbeatDb(
        assets=[FakeAsset(id=1, status_atual="offline")],
        telemetry=[FakeTelemetry(1, 1_000_000)],
        calls=[call],
    )

    executar_verificacao_isolada(db, agora=1_000_000)

    assert call.status == "Novo"
    assert db.added == []


def test_categoria_heartbeat_incompativel_nao_ganha_sla_inferido():
    db = FakeHeartbeatDb(
        assets=[FakeAsset(id=1, status_atual="online")],
        telemetry=[FakeTelemetry(1, 99_999)],
        category=FakeCategory(id=1, sla_horas="valor-existente"),
    )

    executar_verificacao_isolada(db, agora=1_000_000)

    assert db.added[0].sla_horas_aplicado == "valor-existente"


def test_categoria_heartbeat_ausente_nao_cria_fallback():
    db = FakeHeartbeatDb(
        assets=[FakeAsset(id=1, status_atual="online")],
        telemetry=[FakeTelemetry(1, 99_999)],
        category=None,
    )

    with pytest.raises(LookupError, match="categoria heartbeat ausente"):
        executar_verificacao_isolada(db, agora=1_000_000)

    assert db.added == []


def test_fonte_preserva_limite_e_campos_da_criacao_automatica():
    fonte = HEARTBEAT_XS.read_text(encoding="utf-8")

    assert 'add_secs_to_timestamp:-900' in fonte
    assert 'origem               : "automatico"' in fonte
    assert 'criado_em            : "now"' in fonte
    assert 'sla_horas_aplicado   : $categoria_heartbeat.sla_horas' in fonte
    assert 'status               : "Novo"' in fonte
    assert 'prioridade           : "Urgente"' in fonte
