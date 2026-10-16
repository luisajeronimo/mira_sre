// Contrato único e transacional da tratativa operacional, sem reutilizar os
// comandos imediatos legados de responsável.
query "tecnico/chamados/{chamados_id}/tratativa" verb=POST {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    int chamados_id filters=min:1
    int? tecnico_id?
    text status filters=trim
    text prioridade filters=trim
    int categorias_servico_id filters=min:1
    timestamp ultima_atualizacao_em
    text? comentario_status? filters=trim
    text? visibilidade_comentario_status? filters=trim
  }

  stack {
    function.run "service_desk/validar_save_tratativa_chamado" {
      input = {
        usuarios_id: $auth.id
        chamados_id: $input.chamados_id
        tecnico_id: $input.tecnico_id
        status: $input.status
        prioridade: $input.prioridade
        categorias_servico_id: $input.categorias_servico_id
        ultima_atualizacao_em: $input.ultima_atualizacao_em
        comentario_status: $input.comentario_status
        visibilidade_comentario_status: $input.visibilidade_comentario_status
      }
    } as $resultado
  }

  response = $resultado
  guid = "miraSalvarTratativaPost01"
}
