query "simulator/controle-telemetria" verb=GET {
  api_group = "APIS from table telemetria_equipamentos"
  input {
    int[] ativos_referencia_ids
  }
  stack {
    var $resultado { value = {error: "Não autenticado."} }
    var $chave_configurada {
      value = $env.MIRA_SIMULATOR_AUTOMATION_KEY
      mock = {"endpoint controle - chave ausente": "simulator-teste", "endpoint controle - chave incorreta": "simulator-teste", "endpoint controle - chave fiscal negada": "simulator-teste", "endpoint controle - chave valida": "simulator-teste"}
    }
    var $chave {
      value = $env.$http_headers|get:"X-Mira-Simulator-Key"
      mock = {"endpoint controle - chave ausente": null, "endpoint controle - chave incorreta": "incorreta", "endpoint controle - chave fiscal negada": "fiscal-teste", "endpoint controle - chave valida": "simulator-teste"}
    }
    conditional {
      if ($chave_configurada == null || $chave_configurada == "" || $chave == null || $chave == "" || $chave !== $chave_configurada) {
        util.set_header {
          value = "HTTP/1.1 401 Unauthorized"
          duplicates = "replace"
        }
      }
      else {
        function.run "simulator/ler_controles" {
          input = {ativos_referencia_ids: $input.ativos_referencia_ids}
          mock = {"endpoint controle - chave ausente": {leitura_indevida: true}, "endpoint controle - chave incorreta": {leitura_indevida: true}, "endpoint controle - chave fiscal negada": {leitura_indevida: true}, "endpoint controle - chave valida": {items: [{id: 1, telemetria_simulada_ativa: false}]}}
        } as $controles
        var.update $resultado { value = $controles }
      }
    }
  }
  response = $resultado
  test "endpoint controle - chave ausente" {
    input = {ativos_referencia_ids: [1]}
    expect.to_equal ($response) { value = {error: "Não autenticado."} }
  }
  test "endpoint controle - chave incorreta" {
    input = {ativos_referencia_ids: [1]}
    expect.to_equal ($response) { value = {error: "Não autenticado."} }
  }
  test "endpoint controle - chave fiscal negada" {
    input = {ativos_referencia_ids: [1]}
    expect.to_equal ($response) { value = {error: "Não autenticado."} }
  }
  test "endpoint controle - chave valida" {
    input = {ativos_referencia_ids: [1]}
    expect.to_equal ($response) { value = {items: [{id: 1, telemetria_simulada_ativa: false}]} }
  }
  guid = "miraSimulacaoControleEndpoint01"
}
