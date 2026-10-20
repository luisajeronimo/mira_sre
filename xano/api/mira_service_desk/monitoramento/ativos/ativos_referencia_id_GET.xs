// Detalhe operacional de um Totem; Gerente não recebe este contrato.
query "monitoramento/ativos/{ativos_referencia_id}" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    int ativos_referencia_id filters=min:1
  }

  stack {
    function.run "service_desk/obter_detalhe_ativo_monitoramento" {
      input = {usuarios_id: $auth.id, ativos_referencia_id: $input.ativos_referencia_id}
    } as $resultado
  }

  response = $resultado
  guid = "sgy8018Ce_SSyyZU7LHMRsN_gS4"
}
