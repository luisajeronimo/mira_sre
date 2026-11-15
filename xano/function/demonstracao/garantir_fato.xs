// Somente INSERT de fatos do plano nos IDs existentes; sem escrita de cadastro.
function "demonstracao/garantir_fato" {
  input {
    int ativos_referencia_id
    text tipo
    json dados
  }
  stack {
    precondition (($input.ativos_referencia_id == 1 || $input.ativos_referencia_id == 2) && $input.dados.ativos_referencia_id == $input.ativos_referencia_id && ($input.tipo == "telemetria" || $input.tipo == "transicao")) {
      error_type = "inputerror"
      error = "Destino fora do plano autorizado."
    }
    var $rows { value = [] }
    conditional {
      if ($input.tipo == "telemetria") {
        db.query telemetria_equipamentos {
          where = $db.telemetria_equipamentos.ativos_referencia_id == $input.ativos_referencia_id && $db.telemetria_equipamentos.evento_timestamp == $input.dados.evento_timestamp
          return = {type: "list"}
        } as $encontrados
        var.update $rows { value = $encontrados }
      }
      else {
        db.query historico_disponibilidade_totens {
          where = $db.historico_disponibilidade_totens.ativos_referencia_id == $input.ativos_referencia_id && $db.historico_disponibilidade_totens.detectado_em == $input.dados.detectado_em && $db.historico_disponibilidade_totens.status == $input.dados.status
          return = {type: "list"}
        } as $encontrados
        var.update $rows { value = $encontrados }
      }
    }
    api.lambda {
      code = """
        if($var.rows.length>1||$var.rows.some(x=>Object.entries($input.dados).some(([k,v])=>x[k]!==v)))
          throw new Error('Fato duplicado ou divergente; nenhuma substituição.');
        return $var.rows.length?$var.rows[0]:null;
        """
      timeout = 10
    } as $existente
    var $registro { value = $existente }
    conditional {
      if ($existente == null) {
        conditional {
          if ($input.tipo == "telemetria") {
            db.add telemetria_equipamentos {
              data = {ativos_referencia_id: $input.ativos_referencia_id, evento_timestamp: $input.dados.evento_timestamp, uso_cpu: $input.dados.uso_cpu, uso_memoria: $input.dados.uso_memoria, temperatura: $input.dados.temperatura, status_rede: $input.dados.status_rede}
            } as $novo
            var.update $registro { value = $novo }
          }
          else {
            db.add historico_disponibilidade_totens {
              data = {ativos_referencia_id: $input.ativos_referencia_id, status: $input.dados.status, detectado_em: $input.dados.detectado_em, telemetria_referencia_id: $input.dados.telemetria_referencia_id, heartbeat_limite_minutos: 15}
            } as $novo
            var.update $registro { value = $novo }
          }
        }
      }
    }
  }
  response = {id: $registro.id, criado: $existente == null}
  guid = "miraDemoGarantirFato02"
}
