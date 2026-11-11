// Rejeição de solução de chamado Resolvido pelo Gerente da Loja.
query "gerente/chamados/{chamados_id}/rejeitar-solucao" verb=POST {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    int chamados_id filters=min:1
    text justificativa?
    timestamp? ultima_atualizacao_em?
  }

  stack {
    function.run "service_desk/rejeitar_solucao_chamado_gerente" {
      input = {
        usuarios_id: $auth.id
        chamados_id: $input.chamados_id
        justificativa: $input.justificativa
        ultima_atualizacao_em: $input.ultima_atualizacao_em
      }
    } as $resultado
  }

  response = $resultado
  guid = "miraRejeitarSolucaoEndpoint01"
}
