// Query all verificar_falhas records
query verificar_falhas verb=GET {
  api_group = "APIS from table telemetria_equipamentos"

  input {
  }

  stack {
    db.query "" {
      return = {type: "list"}
    } as $verificar_falhas
  }

  response = $verificar_falhas
  guid = "FtYSAIPtJS4jitjytd29h0cssBs"
}