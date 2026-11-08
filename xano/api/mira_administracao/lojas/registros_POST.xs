// Criação administrativa de Loja; a situação inicial pertence ao backend.
query "administracao/lojas/registros" verb=POST {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
    text nome filters=trim|min:1
    text endereco filters=trim|min:1
    text regiao filters=trim|min:1
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id, administrador: true}
    } as $administrador

    db.add lojas {
      data = {
        nome: $input.nome
        endereco: $input.endereco
        regiao: $input.regiao
        status: "Ativa"
      }
    } as $loja

    var $resposta {
      value = {
        id: $loja.id
        nome: $loja.nome
        endereco: $loja.endereco
        regiao: $loja.regiao
        status: $loja.status
      }
    }
  }

  response = $resposta
  guid = "admin-lojas-criar-5a1f4c7d"
}
