// Cenários da prova E0.3: escrita dentro de `db.transaction` seguida de falha.
// O teste de workflow lê a tabela depois da chamada e verifica o efeito parcial.
// `controle_sem_transacao` mostra que o teste detecta persistência quando não há
// transação. Somente dados fictícios em `e03_prova`.
function "e03/executar_cenario" {
  input {
    text cenario
    text marcador
  }

  stack {
    conditional {
      if ($input.cenario == "controle_sem_transacao") {
        db.add e03_prova {
          data = {rotulo: $input.marcador, valor: 1}
        } as $controle

        precondition (false) {
          error_type = "standard"
          error = "Falha após escrita sem transação."
        }
      }

      elseif ($input.cenario == "add_precondition_standard") {
        db.transaction {
          stack {
            db.add e03_prova {
              data = {rotulo: $input.marcador, valor: 1}
            } as $registro

            precondition (false) {
              error_type = "standard"
              error = "Falha após db.add."
            }
          }
        }
      }

      elseif ($input.cenario == "add_precondition_inputerror") {
        db.transaction {
          stack {
            db.add e03_prova {
              data = {rotulo: $input.marcador, valor: 1}
            } as $registro

            precondition (false) {
              error_type = "inputerror"
              error = "Falha após db.add."
            }
          }
        }
      }

      elseif ($input.cenario == "add_throw") {
        db.transaction {
          stack {
            db.add e03_prova {
              data = {rotulo: $input.marcador, valor: 1}
            } as $registro

            throw {
              name = "E03Falha"
              value = "Falha após db.add."
            }
          }
        }
      }

      elseif ($input.cenario == "add_function_run_erro") {
        db.transaction {
          stack {
            db.add e03_prova {
              data = {rotulo: $input.marcador, valor: 1}
            } as $registro

            function.run "e03/falhar" as $nunca
          }
        }
      }

      elseif ($input.cenario == "patch_precondition") {
        db.add e03_prova {
          data = {rotulo: $input.marcador, valor: 0}
        } as $base

        db.transaction {
          stack {
            db.patch e03_prova {
              field_name = "id"
              field_value = $base.id
              data = {valor: 1}
            } as $alterado

            precondition (false) {
              error_type = "standard"
              error = "Falha após db.patch."
            }
          }
        }
      }

      elseif ($input.cenario == "duas_escritas_segunda_falha") {
        db.transaction {
          stack {
            db.add e03_prova {
              data = {rotulo: $input.marcador, valor: 1}
            } as $primeira

            db.add e03_prova {
              data = {rotulo: $input.marcador, valor: 2}
            } as $segunda
          }
        }
      }

      else {
        throw {
          name = "E03CenarioDesconhecido"
          value = "Cenário desconhecido."
        }
      }
    }
  }

  response = null
  guid = "miraProvaE03Cenario01"
}
