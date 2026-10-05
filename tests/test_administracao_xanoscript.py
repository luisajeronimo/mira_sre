"""Harness local dos contratos XanoScript de administração, sem dados reais."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
USUARIOS = (ROOT / "xano/table/usuarios.xs").read_text(encoding="utf-8")
CRIACAO = (ROOT / "xano/api/mira_administracao/usuarios_POST.xs").read_text(encoding="utf-8")
LOGIN = (ROOT / "xano/api/mira_auth/login_POST.xs").read_text(encoding="utf-8")
TROCA = (ROOT / "xano/api/mira_auth/primeiro_acesso_trocar_senha_POST.xs").read_text(encoding="utf-8")
PERFIL = (ROOT / "xano/function/autorizacao/exigir_perfil.xs").read_text(encoding="utf-8")
IDENTIDADE = (ROOT / "xano/function/autorizacao/obter_identidade.xs").read_text(encoding="utf-8")
ESCOPO = (ROOT / "xano/function/autorizacao/exigir_escopo_loja.xs").read_text(encoding="utf-8")
CRUD = (ROOT / "xano/api/apis_from_table_usuarios/usuarios_POST.xs").read_text(encoding="utf-8")
OPCOES_LOJAS_API = (ROOT / "xano/api/mira_administracao/lojas_GET.xs").read_text(encoding="utf-8")
OPCOES_LOJAS = (ROOT / "xano/function/administracao/listar_opcoes_lojas.xs").read_text(encoding="utf-8")
VALIDACAO_CRIACAO = (ROOT / "xano/function/administracao/validar_criacao_usuario.xs").read_text(encoding="utf-8")
LOJAS_GERAL = (ROOT / "xano/api/apis_from_table_lojas/lojas_GET.xs").read_text(encoding="utf-8")
LOJA_POR_ID = (ROOT / "xano/api/apis_from_table_lojas/lojas/lojas_id_GET.xs").read_text(encoding="utf-8")


def test_schema_tem_administrador_sem_ressuscitar_admin_e_flag_compativel():
    assert '"administrador"' in USUARIOS
    assert '"admin"' not in USUARIOS
    assert "bool deve_trocar_senha?=false" in USUARIOS


def test_criacao_e_exclusiva_de_admin_e_nao_expoe_segredo_no_dto():
    assert 'query "administracao/usuarios" verb=POST' in CRIACAO
    assert 'auth = "usuarios"' in CRIACAO
    assert "administrador: true" in CRIACAO
    assert "senha_temporaria filters=min:8" in CRIACAO
    assert "sensitive = true" in CRIACAO
    assert "deve_trocar_senha: true" in CRIACAO
    resposta = CRIACAO.split("var $resposta", 1)[1]
    assert "\n        senha:" not in resposta
    assert "senha_temporaria" not in resposta
    assert "authToken" not in resposta
    assert CRIACAO.index('function.run "autorizacao/exigir_perfil"') < CRIACAO.index(
        'function.run "administracao/validar_criacao_usuario"'
    ) < CRIACAO.index("db.add usuarios")


def test_criacao_valida_matriz_de_loja_e_email_unico():
    assert 'function.run "administracao/validar_criacao_usuario"' in CRIACAO
    assert '$input.role == "gerente"' in VALIDACAO_CRIACAO
    assert "$input.lojas_id == null" in VALIDACAO_CRIACAO
    assert "db.get lojas" in VALIDACAO_CRIACAO
    assert "E-mail já cadastrado." in VALIDACAO_CRIACAO


def test_funcao_de_validacao_testa_regras_sem_escrever_registros():
    assert "db.add" not in VALIDACAO_CRIACAO
    assert 'test "aceita gerente com loja existente"' in VALIDACAO_CRIACAO
    assert 'test "aceita tecnico sem loja"' in VALIDACAO_CRIACAO
    assert 'test "aceita diretoria sem loja"' in VALIDACAO_CRIACAO
    assert 'test "aceita administrador sem loja"' in VALIDACAO_CRIACAO
    assert 'test "rejeita perfil admin legado"' in VALIDACAO_CRIACAO
    assert 'test "rejeita gerente sem loja"' in VALIDACAO_CRIACAO
    assert 'test "rejeita gerente loja inexistente"' in VALIDACAO_CRIACAO
    assert 'test "rejeita tecnico com loja"' in VALIDACAO_CRIACAO
    assert 'test "rejeita diretoria com loja"' in VALIDACAO_CRIACAO
    assert 'test "rejeita administrador com loja"' in VALIDACAO_CRIACAO
    assert 'test "rejeita email duplicado"' in VALIDACAO_CRIACAO


def test_login_e_me_cobrem_administrador_pendente_sem_expor_senha():
    assert 'test "aceita administrador pendente"' in LOGIN
    assert '"aceita administrador pendente"' in LOGIN
    assert 'expect.to_be_defined ($response.authToken)' in LOGIN
    assert 'expect.to_not_be_defined ($response.senha)' in LOGIN
    assert 'test "login rejeita admin legado"' in LOGIN
    assert 'test "retorna identidade administrador pendente"' in IDENTIDADE
    assert "deve_trocar_senha: $usuario.deve_trocar_senha" in IDENTIDADE
    assert 'expect.to_be_true ($response.deve_trocar_senha)' in IDENTIDADE
    assert 'expect.to_not_be_defined ($response.senha)' in IDENTIDADE


def test_gate_central_bloqueia_operacoes_humanas_pendentes():
    for fonte in (PERFIL, ESCOPO):
        assert "$usuario.deve_trocar_senha != true" in fonte
    assert "negar_mutacao_generica" in CRUD


def test_troca_usa_apenas_auth_id_e_atualiza_senha_e_flag_em_transacao():
    assert "usuario_id" not in TROCA
    assert "email" not in TROCA
    assert "$auth.id" in TROCA
    assert "nova_senha filters=min:8" in TROCA
    assert "db.transaction" in TROCA
    assert "senha: $input.nova_senha" in TROCA
    assert "deve_trocar_senha: false" in TROCA


def test_endpoint_opcoes_lojas_e_especifico_da_administracao_e_autenticado():
    assert 'query "administracao/lojas" verb=GET' in OPCOES_LOJAS_API
    assert 'api_group = "MIRA Auth"' in OPCOES_LOJAS_API
    assert 'auth = "usuarios"' in OPCOES_LOJAS_API
    assert 'function.run "administracao/listar_opcoes_lojas"' in OPCOES_LOJAS_API
    assert "usuarios_id: $auth.id" in OPCOES_LOJAS_API
    assert "response = $opcoes" in OPCOES_LOJAS_API


def test_opcoes_lojas_aplicam_gate_admin_e_retornam_apenas_id_e_nome():
    assert 'function.run "autorizacao/exigir_perfil"' in OPCOES_LOJAS
    assert "administrador: true" in OPCOES_LOJAS
    assert 'db.query lojas' in OPCOES_LOJAS
    projecao = OPCOES_LOJAS.split("value = $lojas|map:{", 1)[1].split("}", 1)[0]
    assert "id: $$.id" in projecao
    assert "nome: $$.nome" in projecao
    assert "endereco" not in projecao
    assert "status" not in projecao
    for caso in (
        'test "lista opcoes para administrador concluido"',
        'test "bloqueia administrador pendente"',
        'test "bloqueia gerente"',
        'test "bloqueia tecnico"',
        'test "bloqueia diretoria"',
    ):
        assert caso in OPCOES_LOJAS
        nome_caso = caso.removeprefix('test "').removesuffix('"')
        assert f'"{nome_caso}"' in PERFIL
    assert "deve_trocar_senha: true" in PERFIL
    assert 'test "exigir perfil administrador concluido"' in PERFIL
    assert 'test "exigir perfil administrador pendente"' in PERFIL
    assert 'test "exigir perfil bloqueia gerente"' in PERFIL
    assert 'test "exigir perfil bloqueia tecnico"' in PERFIL
    assert 'test "exigir perfil bloqueia diretoria"' in PERFIL


def test_leitura_geral_de_lojas_preserva_permissoes_anteriores():
    assert 'query lojas verb=GET' in LOJAS_GERAL
    assert 'query "lojas/{lojas_id}" verb=GET' in LOJA_POR_ID
    assert "administrador" not in LOJAS_GERAL
    assert "administrador" not in LOJA_POR_ID
    assert "gerente: true" in LOJAS_GERAL
    assert "diretoria: true" in LOJAS_GERAL
    assert "diretoria: true" in LOJA_POR_ID
