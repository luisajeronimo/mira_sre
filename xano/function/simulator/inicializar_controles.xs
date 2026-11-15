// Operação exclusiva da CLI: prévia padrão e inicialização somente de campos nulos.
function "simulator/inicializar_controles" {
  input {
    int[] ativos_referencia_ids
    int? ativo_silenciado_id?
    bool aplicar?
  }
  stack {
    precondition (($input.ativos_referencia_ids|count) > 0) {
      error_type = "inputerror"
      error = "Informe os Totens participantes."
    }
    var $items { value = [] }
    foreach ($input.ativos_referencia_ids) {
      each as $id {
        db.get ativos_referencia {
          field_name = "id"
          field_value = $id
          mock = {
            "inicializar controle - previa sem escrita": {id: 1, telemetria_simulada_ativa: null}
            "inicializar controle - preserva retomada": {id: 1, telemetria_simulada_ativa: true}
            "inicializar controle - preserva silencio": {id: 1, telemetria_simulada_ativa: false}
            "inicializar controle - inicializa silenciado": {id: 1, telemetria_simulada_ativa: null}
          }
        } as $ativo
        precondition ($id > 0 && $ativo != null) {
          error_type = "inputerror"
          error = "Totem participante não encontrado."
        }
        array.push $items {
          value = {id: $id, anterior: $ativo.telemetria_simulada_ativa, proposto: $ativo.telemetria_simulada_ativa === null ? ($id != $input.ativo_silenciado_id) : $ativo.telemetria_simulada_ativa}
        }
      }
    }
    conditional {
      if ($input.aplicar) {
        foreach ($items) {
          each as $item {
            conditional {
              if ($item.anterior === null) {
                db.get ativos_referencia {
                  field_name = "id"
                  field_value = $item.id
                  mock = {"inicializar controle - inicializa silenciado": {id: 1, telemetria_simulada_ativa: null}}
                } as $atual
                conditional {
                  if ($atual.telemetria_simulada_ativa === null) {
                    db.edit ativos_referencia {
                      field_name = "id"
                      field_value = $item.id
                      data = {telemetria_simulada_ativa: $item.proposto}
                      mock = {"inicializar controle - inicializa silenciado": {id: 1, telemetria_simulada_ativa: false}}
                    } as $salvo
                  }
                }
              }
            }
          }
        }
      }
    }
  }
  response = {items: $items, aplicado: $input.aplicar}
  test "inicializar controle - previa sem escrita" {
    input = {ativos_referencia_ids: [1], aplicar: false}
    expect.to_equal ($response.items) { value = [{id: 1, anterior: null, proposto: true}] }
    expect.to_equal ($response.aplicado) { value = false }
  }
  test "inicializar controle - preserva retomada" {
    input = {ativos_referencia_ids: [1], ativo_silenciado_id: 1, aplicar: true}
    expect.to_equal ($response.items) { value = [{id: 1, anterior: true, proposto: true}] }
  }
  test "inicializar controle - inicializa silenciado" {
    input = {ativos_referencia_ids: [1], ativo_silenciado_id: 1, aplicar: true}
    expect.to_equal ($response.items) { value = [{id: 1, anterior: null, proposto: false}] }
  }
  test "inicializar controle - preserva silencio" {
    input = {ativos_referencia_ids: [1], aplicar: true}
    expect.to_equal ($response.items) { value = [{id: 1, anterior: false, proposto: false}] }
  }
  guid = "miraSimulacaoInicializar01"
}
