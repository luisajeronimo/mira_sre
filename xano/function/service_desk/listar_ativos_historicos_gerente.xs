// Catálogo de filtro: inclui Totens com vínculo comprovado à Loja do Gerente.
function "service_desk/listar_ativos_historicos_gerente" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, gerente: true}
    } as $gerente

    precondition ($gerente.lojas_id != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    db.query ativos_referencia {
      sort = {ativos_referencia.id: "asc"}
      return = {type: "list"}
    } as $totens

    var $items {
      value = []
    }

    foreach ($totens) {
      each as $totem {
        db.query historico_vinculos_totem_loja {
          where = $db.historico_vinculos_totem_loja.ativos_referencia_id == $totem.id && $db.historico_vinculos_totem_loja.loja_destino_id == $gerente.lojas_id
          return = {type: "exists"}
        } as $passou_pela_loja

        conditional {
          if ($totem.lojas_id == $gerente.lojas_id || $passou_pela_loja) {
            array.push $items {
              value = {
                id          : $totem.id
                nome_ativo  : $totem.nome_ativo
                tipo        : $totem.tipo
                status_atual: $totem.status_atual
              }
            }
          }
        }
      }
    }
  }

  response = {items: $items}
  guid = "miraAtivosHistoricosGerente01"
}