// Fornece opções mínimas de Loja apenas ao fluxo administrativo de Gerente.
query "administracao/lojas" verb=GET {
  api_group = "MIRA Auth"
  auth = "usuarios"
  description = "Opções mínimas de Loja para criação administrativa de Gerente."

  input {
  }

  stack {
    function.run "administracao/listar_opcoes_lojas" {
      input = {usuarios_id: $auth.id}
    } as $opcoes
  }

  response = $opcoes
  guid = "xW9DYsHD7OcK_dQP5SI6otU88Zo"
}
