// A retomada muda apenas o controle; o Fiscal permanece responsável pela recuperação.
function "service_desk/retomar_telemetria" {
  input {
    int usuarios_id
    int ativos_referencia_id
  }
  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
        "retomada - tecnico retoma": {role: "tecnico", deve_trocar_senha: false}
        "retomada - diretoria retoma": {role: "diretoria", deve_trocar_senha: false}
        "retomada - administrador retoma": {role: "administrador", deve_trocar_senha: false}
        "retomada - repeticao idempotente": {role: "tecnico", deve_trocar_senha: false}
        "retomada - estado incompativel": {role: "tecnico", deve_trocar_senha: false}
        "retomada - nao gerenciado": {role: "tecnico", deve_trocar_senha: false}
        "retomada - totem inexistente": {role: "tecnico", deve_trocar_senha: false}
        "retomada - sessao invalida": null
        "retomada - gerente negado": {role: "gerente", deve_trocar_senha: false}
        "retomada - troca pendente": {role: "administrador", deve_trocar_senha: true}
      }
    } as $usuario
    precondition (($usuario.role == "tecnico" || $usuario.role == "diretoria" || $usuario.role == "administrador") && $usuario.deve_trocar_senha === false) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }
    db.get ativos_referencia {
      field_name = "id"
      field_value = $input.ativos_referencia_id
      mock = {
        "retomada - tecnico retoma": {id: 1, status_atual: "offline", telemetria_simulada_ativa: false}
        "retomada - diretoria retoma": {id: 1, status_atual: "offline", telemetria_simulada_ativa: false}
        "retomada - administrador retoma": {id: 1, status_atual: "offline", telemetria_simulada_ativa: false}
        "retomada - repeticao idempotente": {id: 1, status_atual: "online", telemetria_simulada_ativa: true}
        "retomada - estado incompativel": {id: 1, status_atual: "online", telemetria_simulada_ativa: false}
        "retomada - nao gerenciado": {id: 1, status_atual: "offline", telemetria_simulada_ativa: null}
        "retomada - totem inexistente": null
      }
    } as $ativo
    precondition ($ativo != null) {
      error_type = "notfound"
      error = "Totem não encontrado."
    }
    var $autorizado { value = $ativo.telemetria_simulada_ativa === true }
    conditional {
      if ($ativo.telemetria_simulada_ativa === false && $ativo.status_atual == "offline") {
        db.edit ativos_referencia {
          field_name = "id"
          field_value = $ativo.id
          data = {telemetria_simulada_ativa: true}
          mock = {
            "retomada - tecnico retoma": {id: 1, telemetria_simulada_ativa: true}
            "retomada - diretoria retoma": {id: 1, telemetria_simulada_ativa: true}
            "retomada - administrador retoma": {id: 1, telemetria_simulada_ativa: true}
          }
        } as $salvo
        var.update $autorizado { value = true }
      }
    }
  }
  response = {id: $ativo.id, envio_autorizado: $autorizado, status_atual: $ativo.status_atual}
  test "retomada - tecnico retoma" {
    input = {usuarios_id: 12, ativos_referencia_id: 1}
    expect.to_equal ($response.envio_autorizado) { value = true }
    expect.to_equal ($response.status_atual) { value = "offline" }
  }
  test "retomada - diretoria retoma" {
    input = {usuarios_id: 12, ativos_referencia_id: 1}
    expect.to_equal ($response.envio_autorizado) { value = true }
  }
  test "retomada - administrador retoma" {
    input = {usuarios_id: 12, ativos_referencia_id: 1}
    expect.to_equal ($response.envio_autorizado) { value = true }
  }
  test "retomada - repeticao idempotente" {
    input = {usuarios_id: 12, ativos_referencia_id: 1}
    expect.to_equal ($response.envio_autorizado) { value = true }
    expect.to_equal ($response.status_atual) { value = "online" }
  }
  test "retomada - estado incompativel" {
    input = {usuarios_id: 12, ativos_referencia_id: 1}
    expect.to_equal ($response.envio_autorizado) { value = false }
  }
  test "retomada - nao gerenciado" {
    input = {usuarios_id: 12, ativos_referencia_id: 1}
    expect.to_equal ($response.envio_autorizado) { value = false }
  }
  test "retomada - gerente negado" {
    input = {usuarios_id: 12, ativos_referencia_id: 1}
    expect.to_throw
  }
  test "retomada - troca pendente" {
    input = {usuarios_id: 12, ativos_referencia_id: 1}
    expect.to_throw
  }
  test "retomada - totem inexistente" {
    input = {usuarios_id: 12, ativos_referencia_id: 1}
    expect.to_throw
  }
  test "retomada - sessao invalida" {
    input = {usuarios_id: 0, ativos_referencia_id: 1}
    expect.to_throw
  }
  guid = "miraRetomarTelemetria01"
}
