// Cria um usuário humano pelo fluxo administrativo aprovado.
query "administracao/usuarios" verb=POST {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
    text nome filters=trim|min:1
    email email filters=trim|lower
    text role filters=trim
    int? lojas_id? filters=min:1
    text senha_temporaria filters=min:8 {
      sensitive = true
    }
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id, administrador: true}
    } as $administrador

    function.run "administracao/validar_criacao_usuario" {
      input = {
        email: $input.email
        role: $input.role
        lojas_id: $input.lojas_id
      }
    } as $validacao

    db.add usuarios {
      data = {
        nome: $input.nome
        email: $input.email
        role: $input.role
        lojas_id: $input.lojas_id
        senha: $input.senha_temporaria
        deve_trocar_senha: true
      }
    } as $usuario_criado

    var $resposta {
      value = {
        id: $usuario_criado.id
        nome: $usuario_criado.nome
        email: $usuario_criado.email
        role: $usuario_criado.role
        lojas_id: $usuario_criado.lojas_id
        deve_trocar_senha: $usuario_criado.deve_trocar_senha
      }
    }
  }

  response = $resposta
  guid = "aK7mN2pQ4rS8tV1wX5yZ3bC6dE"
}
