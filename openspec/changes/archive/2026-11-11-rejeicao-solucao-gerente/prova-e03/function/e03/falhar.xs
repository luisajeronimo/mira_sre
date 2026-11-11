// Função auxiliar da prova E0.3: sempre lança erro, sem escrita.
function "e03/falhar" {
  input {
  }

  stack {
    throw {
      name = "E03Falha"
      value = "Falha provocada pela prova E0.3."
    }
  }

  response = null
  guid = "miraProvaE03Falhar01"
}
