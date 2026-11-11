// Matriz E0.3 no runtime Xano. Usa datasource = "live" com clonagem automática isolada.
// Cada cenário usa um marcador próprio; a leitura posterior conta os registros.
workflow_test "e03_rollback" {
  datasource = "live"

  stack {
    expect.to_throw {
      stack {
        function.call "e03/executar_cenario" {
          input = {cenario: "controle_sem_transacao", marcador: "e03-controle"}
        } as $r0
      }

      exception = ""
    }

    db.query e03_prova {
      where = $db.e03_prova.rotulo == "e03-controle"
      return = {type: "count"}
    } as $controle

    expect.to_equal ($controle) {
      value = 1
    }

    expect.to_throw {
      stack {
        function.call "e03/executar_cenario" {
          input = {cenario: "add_precondition_standard", marcador: "e03-add-standard"}
        } as $r1
      }

      exception = ""
    }

    db.query e03_prova {
      where = $db.e03_prova.rotulo == "e03-add-standard"
      return = {type: "count"}
    } as $add_standard

    expect.to_equal ($add_standard) {
      value = 0
    }

    expect.to_throw {
      stack {
        function.call "e03/executar_cenario" {
          input = {cenario: "add_precondition_inputerror", marcador: "e03-add-inputerror"}
        } as $r2
      }

      exception = ""
    }

    db.query e03_prova {
      where = $db.e03_prova.rotulo == "e03-add-inputerror"
      return = {type: "count"}
    } as $add_inputerror

    expect.to_equal ($add_inputerror) {
      value = 0
    }

    expect.to_throw {
      stack {
        function.call "e03/executar_cenario" {
          input = {cenario: "add_throw", marcador: "e03-add-throw"}
        } as $r3
      }

      exception = ""
    }

    db.query e03_prova {
      where = $db.e03_prova.rotulo == "e03-add-throw"
      return = {type: "count"}
    } as $add_throw

    expect.to_equal ($add_throw) {
      value = 0
    }

    expect.to_throw {
      stack {
        function.call "e03/executar_cenario" {
          input = {cenario: "add_function_run_erro", marcador: "e03-add-function-run"}
        } as $r4
      }

      exception = ""
    }

    db.query e03_prova {
      where = $db.e03_prova.rotulo == "e03-add-function-run"
      return = {type: "count"}
    } as $add_function_run

    expect.to_equal ($add_function_run) {
      value = 0
    }

    expect.to_throw {
      stack {
        function.call "e03/executar_cenario" {
          input = {cenario: "patch_precondition", marcador: "e03-patch"}
        } as $r5
      }

      exception = ""
    }

    db.query e03_prova {
      where = $db.e03_prova.rotulo == "e03-patch" && $db.e03_prova.valor == 0
      return = {type: "count"}
    } as $patch_preservado

    expect.to_equal ($patch_preservado) {
      value = 1
    }

    expect.to_throw {
      stack {
        function.call "e03/executar_cenario" {
          input = {cenario: "duas_escritas_segunda_falha", marcador: "e03-duas-escritas"}
        } as $r6
      }

      exception = ""
    }

    db.query e03_prova {
      where = $db.e03_prova.rotulo == "e03-duas-escritas"
      return = {type: "count"}
    } as $duas_escritas

    expect.to_equal ($duas_escritas) {
      value = 0
    }
  }

  tags = ["e03", "rollback"]
}
