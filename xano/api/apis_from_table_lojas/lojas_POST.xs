// Add lojas record
query lojas verb=POST {
  api_group = "APIS from table lojas"
  auth = "usuarios"

  input {
    dblink {
      table = "lojas"
    }
  }

  stack {
    function.run "autorizacao/negar_mutacao_generica" {
      input = {usuarios_id: $auth.id}
    } as $negado

    db.add lojas {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $lojas
  }

  response = $lojas
  guid = "mFJZNi_pZiHDKqRDNWqWlrbxPSk"
}
