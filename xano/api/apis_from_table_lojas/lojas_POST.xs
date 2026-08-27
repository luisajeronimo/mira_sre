// Add lojas record
query lojas verb=POST {
  api_group = "APIS from table lojas"

  input {
    dblink {
      table = "lojas"
    }
  }

  stack {
    db.add lojas {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $lojas
  }

  response = $lojas
  guid = "mFJZNi_pZiHDKqRDNWqWlrbxPSk"
}