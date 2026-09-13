// Retorna a identidade pública da sessão atual.
query me verb=GET {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "autorizacao/obter_identidade" {
      input = {usuarios_id: $auth.id}
    } as $identidade
  }

  response = $identidade
  guid = "ggY4ElRhekhsXrkCDOhSAx633X8"
}
