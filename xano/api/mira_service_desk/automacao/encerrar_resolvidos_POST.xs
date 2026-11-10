// Encerramento sob comando manual de chamados Resolvidos há 72 horas.
query "automacao/encerrar-resolvidos" verb=POST {
  api_group = "MIRA Service Desk"

  input {
  }

  stack {
    var $chave_recebida {
      value = $env.$http_headers|get:"X-Mira-Encerramento-Key"
    }

    var $chave_configurada {
      value = $env.MIRA_ENCERRAMENTO_AUTOMATION_KEY
    }

    conditional {
      if (!($chave_configurada != null && $chave_configurada != "" && $chave_recebida != null && $chave_recebida != "" && $chave_recebida === $chave_configurada)) {
        util.set_header {
          value = "HTTP/1.1 401 Unauthorized"
          duplicates = "replace"
        }

        precondition (false) {
          error_type = "unauthorized"
          error = "Não autenticado."
        }
      }
    }

    function.run "service_desk/encerrar_chamados_resolvidos_elegiveis" {} as $resultado
  }

  response = $resultado
  guid = "miraEncerrarResolvidosEndpoint01"
}
