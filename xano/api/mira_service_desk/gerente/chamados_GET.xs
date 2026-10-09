// Lista funcional de chamados da Loja do Gerente.
query "gerente/chamados" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    // A fronteira HTTP recebe os identificadores como texto para distinguir
    // ausência (string vazia) de `0` explicitamente informado no runtime.
    text numero? filters=trim
    text status? filters=trim
    text ativo_id? filters=trim
    timestamp data_inicio?
    timestamp data_fim?
    text ordenar_por? filters=trim
    text direcao? filters=trim
  }

  stack {
    function.run "service_desk/listar_chamados_gerente" {
      input = {
        usuarios_id: $auth.id,
        numero: $input.numero,
        status: $input.status,
        ativo_id: $input.ativo_id,
        data_inicio: $input.data_inicio,
        data_fim: $input.data_fim,
        ordenar_por: $input.ordenar_por,
        direcao: $input.direcao
      }
    } as $resultado
  }

  response = $resultado
  guid = "6h4T1Nwn7Coht05btWyScvCe-K8"
}
