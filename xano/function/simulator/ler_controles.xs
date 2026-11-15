// Consulta agrupada, sem alterar disponibilidade ou fatos operacionais.
function "simulator/ler_controles" {
  input {
    int[] ativos_referencia_ids
  }
  stack {
    precondition (($input.ativos_referencia_ids|count) > 0) {
      error_type = "inputerror"
      error = "Informe os Totens participantes."
    }
    var $items { value = [] }
    foreach ($input.ativos_referencia_ids) {
      each as $id {
        precondition ($id > 0) {
          error_type = "inputerror"
          error = "Identificador de Totem inválido."
        }
        db.get ativos_referencia {
          field_name = "id"
          field_value = $id
          mock = {
            "ler controle - controle ativo": {id: 1, telemetria_simulada_ativa: true}
            "ler controle - controle silenciado": {id: 1, telemetria_simulada_ativa: false}
            "ler controle - controle ausente": {id: 1, telemetria_simulada_ativa: null}
            "ler controle - totem inexistente": null
          }
        } as $ativo
        conditional {
          if ($ativo != null) {
            array.push $items {
              value = {id: $ativo.id, telemetria_simulada_ativa: $ativo.telemetria_simulada_ativa}
            }
          }
        }
      }
    }
  }
  response = {items: $items}
  test "ler controle - controle ativo" {
    input = {ativos_referencia_ids: [1]}
    expect.to_equal ($response.items) { value = [{id: 1, telemetria_simulada_ativa: true}] }
  }
  test "ler controle - controle silenciado" {
    input = {ativos_referencia_ids: [1]}
    expect.to_equal ($response.items) { value = [{id: 1, telemetria_simulada_ativa: false}] }
  }
  test "ler controle - controle ausente" {
    input = {ativos_referencia_ids: [1]}
    expect.to_equal ($response.items) { value = [{id: 1, telemetria_simulada_ativa: null}] }
  }
  test "ler controle - totem inexistente" {
    input = {ativos_referencia_ids: [1]}
    expect.to_equal ($response.items) { value = [] }
  }
  guid = "miraSimulacaoLerControles01"
}
