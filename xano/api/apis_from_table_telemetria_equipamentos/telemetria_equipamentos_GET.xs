// Query all telemetria_equipamentos records
query telemetria_equipamentos verb=GET {
  api_group = "APIS from table telemetria_equipamentos"
  auth = "usuarios"

  input {
    int ativos_referencia_id {
      table = "ativos_referencia"
    }
  
    timestamp? data_inicio?
    timestamp? data_fim?
    int limit?=100
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {
        usuarios_id: $auth.id,
        gerente: true,
        tecnico: true,
        diretoria: true
      }
    } as $usuario

    precondition ($usuario.role != "gerente" || $usuario.lojas_id != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    db.query telemetria_equipamentos {
      join = {
        ativo: {
          table: "ativos_referencia",
          type: "inner",
          where: $db.telemetria_equipamentos.ativos_referencia_id == $db.ativo.id
        }
      }
      where = $db.telemetria_equipamentos.ativos_referencia_id == $input.ativos_referencia_id && ($usuario.role == "tecnico" || $usuario.role == "diretoria" || ($usuario.role == "gerente" && $db.ativo.lojas_id == $usuario.lojas_id))
      sort = {telemetria_equipamentos.evento_timestamp: "desc"}
      return = {type: "list"}
      output = [
        "id"
        "ativos_referencia_id"
        "uso_cpu"
        "uso_memoria"
        "temperatura"
        "status_rede"
        "evento_timestamp"
      ]
    } as $telemetria_equipamentos
  }

  response = $telemetria_equipamentos
  guid = "l_HQnw0mBrkXpVcEX8G3PUK8JNo"
}
