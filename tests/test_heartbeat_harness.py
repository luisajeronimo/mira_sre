"""Harness isolado das transições de disponibilidade de ``verificar-falhas``.

O arquivo espelha a regra do endpoint em memória. Ele cobre regressões lógicas
e a sequência estática da transação, mas não prova rollback no runtime Xano.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import pytest


HEARTBEAT_XS = Path(__file__).parents[1] / "xano/api/apis_from_table_telemetria_equipamentos/verificar_falhas_GET.xs"
HISTORY_XS = Path(__file__).parents[1] / "xano/table/historico_disponibilidade_totens.xs"

HEARTBEAT_LIMIT_MS = 900_000
HEARTBEAT_LIMIT_MINUTES = 15
NON_TERMINAL_EQUIVALENT_STATUSES = {
    "Novo",
    "Em Atendimento",
    "Aguardando Solicitante",
    "Aguardando Mudança",
    "Resolvido",
    "Solução Rejeitada",
}


@dataclass
class FakeAsset:
    id: int
    status_atual: str


@dataclass
class FakeTelemetry:
    id: int
    ativos_referencia_id: int
    evento_timestamp: int


@dataclass
class FakeCategory:
    id: int
    sla_horas: Any
    tipo_itil: str = "Incidente"
    permite_abertura_manual: bool = False


@dataclass
class FakeCall:
    ativos_referencia_id: int
    categorias_servico_id: int
    status: str
    prioridade: str
    origem: str | None = None
    criador_sistema: str | None = None
    criado_em: int | None = None
    sla_horas_aplicado: Any = None


@dataclass
class FakeAvailabilityHistory:
    ativos_referencia_id: int
    telemetria_referencia_id: int
    status: str
    detectado_em: int
    heartbeat_limite_minutos: int


@dataclass
class FakeHeartbeatDb:
    assets: list[FakeAsset]
    telemetry: list[FakeTelemetry] = field(default_factory=list)
    category: FakeCategory | None = field(
        default_factory=lambda: FakeCategory(id=1, sla_horas=1)
    )
    calls: list[FakeCall] = field(default_factory=list)
    history: list[FakeAvailabilityHistory] = field(default_factory=list)
    edits: list[tuple[int, str]] = field(default_factory=list)
    added: list[FakeCall] = field(default_factory=list)
    fail_on: str | None = None

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
        return next(
            (
                call
                for call in self.calls + self.added
                if call.ativos_referencia_id == asset_id
                and call.categorias_servico_id == category_id
                and call.status in NON_TERMINAL_EQUIVALENT_STATUSES
            ),
            None,
        )

    def transaction(self, write: Callable[[], bool]) -> bool:
        """Representa a unidade all-or-nothing prevista para o Xano.

        Esta simulação é uma evidência estática de sequência. A task 6.4 deve
        comprovar a semântica equivalente no runtime após push autorizado.
        """

        asset_states = [asset.status_atual for asset in self.assets]
        history = list(self.history)
        edits = list(self.edits)
        added = list(self.added)
        try:
            return write()
        except Exception:
            for asset, status in zip(self.assets, asset_states, strict=True):
                asset.status_atual = status
            self.history = history
            self.edits = edits
            self.added = added
            raise

    def edit_status(self, asset: FakeAsset, status: str) -> None:
        if self.fail_on == "edit_status":
            raise RuntimeError("falha controlada ao atualizar Totem")
        asset.status_atual = status
        self.edits.append((asset.id, status))

    def add_history(self, event: FakeAvailabilityHistory) -> None:
        if self.fail_on == "add_history":
            raise RuntimeError("falha controlada ao criar histórico")
        self.history.append(event)

    def add_call(self, call: FakeCall) -> None:
        if self.fail_on == "add_call":
            raise RuntimeError("falha controlada ao criar chamado")
        self.added.append(call)


def _validar_categoria_heartbeat(categoria: FakeCategory | None) -> FakeCategory:
    if (
        categoria is None
        or categoria.tipo_itil != "Incidente"
        or categoria.sla_horas is None
        or categoria.permite_abertura_manual is not False
    ):
        raise LookupError("categoria heartbeat indisponível ou incompatível")
    return categoria


def executar_verificacao_isolada(
    db: FakeHeartbeatDb,
    *,
    agora: int,
    detectado_em: int = 9_000,
    criado_em: int = 9_000,
) -> dict[str, int]:
    """Espelha transições do endpoint sem tocar recursos remotos."""

    limite = agora - HEARTBEAT_LIMIT_MS
    online = offline = sem_telemetria = incidentes = 0

    for asset in db.assets:
        ultima = db.latest_telemetry(asset.id)
        if ultima is None:
            sem_telemetria += 1
            continue

        if ultima.evento_timestamp < limite:
            if asset.status_atual == "offline":
                offline += 1
                continue
            if asset.status_atual != "online":
                continue

            categoria = _validar_categoria_heartbeat(db.get_heartbeat_category())

            def transicao_offline() -> bool:
                telemetria_revalidada = db.latest_telemetry(asset.id)
                if (
                    asset.status_atual != "online"
                    or telemetria_revalidada is None
                    or telemetria_revalidada.evento_timestamp >= limite
                ):
                    return False
                equivalente = db.open_equivalent(asset.id, categoria.id)
                db.add_history(
                    FakeAvailabilityHistory(
                        ativos_referencia_id=asset.id,
                        telemetria_referencia_id=telemetria_revalidada.id,
                        status="offline",
                        detectado_em=detectado_em,
                        heartbeat_limite_minutos=HEARTBEAT_LIMIT_MINUTES,
                    )
                )
                db.edit_status(asset, "offline")
                if equivalente is None:
                    db.add_call(
                        FakeCall(
                            ativos_referencia_id=asset.id,
                            categorias_servico_id=categoria.id,
                            status="Novo",
                            prioridade="Urgente",
                            origem="automatico",
                            criador_sistema="bot_fiscalizacao",
                            criado_em=criado_em,
                            sla_horas_aplicado=categoria.sla_horas,
                        )
                    )
                    return True
                return False

            incidentes += int(db.transaction(transicao_offline))
            offline += 1
            continue

        if asset.status_atual == "online":
            online += 1
            continue
        if asset.status_atual != "offline":
            continue

        def transicao_online() -> bool:
            telemetria_revalidada = db.latest_telemetry(asset.id)
            if (
                asset.status_atual != "offline"
                or telemetria_revalidada is None
                or telemetria_revalidada.evento_timestamp < limite
            ):
                return False
            db.add_history(
                FakeAvailabilityHistory(
                    ativos_referencia_id=asset.id,
                    telemetria_referencia_id=telemetria_revalidada.id,
                    status="online",
                    detectado_em=detectado_em,
                    heartbeat_limite_minutos=HEARTBEAT_LIMIT_MINUTES,
                )
            )
            db.edit_status(asset, "online")
            return True

        db.transaction(transicao_online)
        online += 1

    return {
        "online": online,
        "offline": offline,
        "sem_telemetria": sem_telemetria,
        "incidentes_criados": incidentes,
    }


def test_ativo_sem_telemetria_preserva_status_sem_historico_ou_incidente():
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
    assert db.history == []
    assert db.added == []


def test_online_com_telemetria_recente_nao_escreve_transicao():
    db = FakeHeartbeatDb(
        assets=[FakeAsset(id=1, status_atual="online")],
        telemetry=[FakeTelemetry(99, 1, 1_000_000)],
    )

    resultado = executar_verificacao_isolada(db, agora=1_000_000)

    assert resultado["online"] == 1
    assert db.edits == []
    assert db.history == []
    assert db.added == []


def test_limite_exatamente_15_minutos_nao_marca_offline():
    db = FakeHeartbeatDb(
        assets=[FakeAsset(id=1, status_atual="online")],
        telemetry=[FakeTelemetry(99, 1, 100_000)],
    )

    resultado = executar_verificacao_isolada(db, agora=1_000_000)

    assert resultado["online"] == 1
    assert db.assets[0].status_atual == "online"
    assert db.history == []


def test_online_para_offline_persiste_fato_e_incidente_automatico():
    db = FakeHeartbeatDb(
        assets=[FakeAsset(id=1, status_atual="online")],
        telemetry=[FakeTelemetry(77, 1, 99_999)],
        category=FakeCategory(id=1, sla_horas=2),
    )

    resultado = executar_verificacao_isolada(
        db, agora=1_000_000, detectado_em=123_456, criado_em=123_456
    )

    assert resultado == {
        "online": 0,
        "offline": 1,
        "sem_telemetria": 0,
        "incidentes_criados": 1,
    }
    assert db.assets[0].status_atual == "offline"
    assert db.history == [
        FakeAvailabilityHistory(1, 77, "offline", 123_456, HEARTBEAT_LIMIT_MINUTES)
    ]
    assert db.added == [
        FakeCall(
            ativos_referencia_id=1,
            categorias_servico_id=1,
            status="Novo",
            prioridade="Urgente",
            origem="automatico",
            criador_sistema="bot_fiscalizacao",
            criado_em=123_456,
            sla_horas_aplicado=2,
        )
    ]


def test_offline_continuo_nao_duplica_historico_ou_incidente():
    db = FakeHeartbeatDb(
        assets=[FakeAsset(id=1, status_atual="online")],
        telemetry=[FakeTelemetry(77, 1, 99_999)],
    )

    executar_verificacao_isolada(db, agora=1_000_000)
    segunda = executar_verificacao_isolada(db, agora=1_000_000)

    assert segunda["offline"] == 1
    assert len(db.history) == 1
    assert len(db.added) == 1


@pytest.mark.parametrize("status", sorted(NON_TERMINAL_EQUIVALENT_STATUSES))
def test_cada_status_nao_terminal_bloqueia_so_o_novo_incidente(status: str):
    existente = FakeCall(1, 1, status, "Urgente")
    db = FakeHeartbeatDb(
        assets=[FakeAsset(id=1, status_atual="online")],
        telemetry=[FakeTelemetry(77, 1, 99_999)],
        calls=[existente],
    )

    resultado = executar_verificacao_isolada(db, agora=1_000_000)

    assert resultado["incidentes_criados"] == 0
    assert db.assets[0].status_atual == "offline"
    assert len(db.history) == 1
    assert db.added == []
    assert existente.criador_sistema is None


@pytest.mark.parametrize("status", ["Encerrado", "Cancelado", "Aguardando Terceiro"])
def test_status_fora_da_chave_nao_bloqueia_nova_criacao(status: str):
    db = FakeHeartbeatDb(
        assets=[FakeAsset(id=1, status_atual="online")],
        telemetry=[FakeTelemetry(77, 1, 99_999)],
        calls=[FakeCall(1, 1, status, "Urgente")],
    )

    resultado = executar_verificacao_isolada(db, agora=1_000_000)

    assert resultado["incidentes_criados"] == 1
    assert len(db.history) == 1
    assert len(db.added) == 1


def test_offline_para_online_persiste_recuperacao_sem_alterar_chamado():
    chamado = FakeCall(1, 1, "Novo", "Urgente", "automatico", None, 100, 2)
    db = FakeHeartbeatDb(
        assets=[FakeAsset(id=1, status_atual="offline")],
        telemetry=[FakeTelemetry(88, 1, 1_000_000)],
        calls=[chamado],
    )

    resultado = executar_verificacao_isolada(
        db, agora=1_000_000, detectado_em=123_456
    )

    assert resultado["online"] == 1
    assert db.assets[0].status_atual == "online"
    assert db.history == [
        FakeAvailabilityHistory(1, 88, "online", 123_456, HEARTBEAT_LIMIT_MINUTES)
    ]
    assert db.added == []
    assert chamado.status == "Novo"


def test_online_continuo_apos_recuperacao_nao_duplica_evento_online():
    db = FakeHeartbeatDb(
        assets=[FakeAsset(id=1, status_atual="offline")],
        telemetry=[FakeTelemetry(88, 1, 1_000_000)],
    )

    executar_verificacao_isolada(db, agora=1_000_000)
    executar_verificacao_isolada(db, agora=1_000_000)

    assert db.assets[0].status_atual == "online"
    assert [event.status for event in db.history] == ["online"]
    assert db.edits == [(1, "online")]


@pytest.mark.parametrize(
    "category",
    [
        None,
        FakeCategory(id=1, sla_horas=None),
        FakeCategory(id=1, sla_horas=1, tipo_itil="Requisição"),
        FakeCategory(id=1, sla_horas=1, permite_abertura_manual=True),
    ],
)
def test_categoria_ausente_ou_incompativel_nao_inicia_transicao(category: FakeCategory | None):
    db = FakeHeartbeatDb(
        assets=[FakeAsset(id=1, status_atual="online")],
        telemetry=[FakeTelemetry(77, 1, 99_999)],
        category=category,
    )

    with pytest.raises(LookupError, match="categoria heartbeat"):
        executar_verificacao_isolada(db, agora=1_000_000)

    assert db.assets[0].status_atual == "online"
    assert db.history == []
    assert db.added == []


def test_falha_controlada_representa_rollback_estatico_e_nova_tentativa():
    db = FakeHeartbeatDb(
        assets=[FakeAsset(id=1, status_atual="online")],
        telemetry=[FakeTelemetry(77, 1, 99_999)],
        fail_on="add_call",
    )

    with pytest.raises(RuntimeError, match="falha controlada"):
        executar_verificacao_isolada(db, agora=1_000_000)

    assert db.assets[0].status_atual == "online"
    assert db.history == []
    assert db.added == []

    db.fail_on = None
    resultado = executar_verificacao_isolada(db, agora=1_000_000)

    assert resultado["incidentes_criados"] == 1
    assert db.assets[0].status_atual == "offline"
    assert len(db.history) == 1


def test_fontes_declaram_schema_transacoes_e_contrato_aprovado():
    endpoint = HEARTBEAT_XS.read_text(encoding="utf-8")
    schema = HISTORY_XS.read_text(encoding="utf-8")

    assert 'db.transaction {' in endpoint
    assert 'as $categoria_heartbeat_revalidada' in endpoint
    assert 'MIRA_FISCAL_AUTOMATION_KEY' in endpoint
    assert 'X-Mira-Fiscal-Key' in endpoint
    assert 'table historico_disponibilidade_totens' in schema
    assert 'int ativos_referencia_id {' in schema
    assert 'table = "ativos_referencia"' in schema
    assert 'int telemetria_referencia_id {' in schema
    assert 'table = "telemetria_equipamentos"' in schema
    assert 'values = ["online", "offline"]' in schema
    assert 'timestamp detectado_em' in schema
    assert 'int heartbeat_limite_minutos' in schema
    assert 'add_secs_to_timestamp:-900' in endpoint
    assert '$ultima_telemetria.evento_timestamp < $limite_heartbeat' in endpoint
    assert '$telemetria_revalidada.evento_timestamp >= $limite_heartbeat' in endpoint
    for status in NON_TERMINAL_EQUIVALENT_STATUSES:
        assert f'$db.chamados.status == "{status}"' in endpoint
    assert 'Aguardando Terceiro' not in endpoint
    assert 'origem               : "automatico"' in endpoint
    assert 'criador_sistema      : "bot_fiscalizacao"' in endpoint
    assert 'criado_em            : "now"' in endpoint
    assert 'sla_horas_aplicado   : $categoria_heartbeat_revalidada.sla_horas' in endpoint
    assert 'status               : "Novo"' in endpoint
    assert 'prioridade           : "Urgente"' in endpoint
