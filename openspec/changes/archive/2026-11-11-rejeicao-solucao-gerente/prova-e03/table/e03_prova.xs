// Tabela exclusiva da prova E0.3. Somente dados fictícios; não pertence ao MIRA.
table e03_prova {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }

    text rotulo filters=trim
    int valor?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "rotulo"}]}
  ]

  guid = "miraProvaE03Tabela01"
}
