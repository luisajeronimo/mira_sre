// Classificação e parâmetro SLA
table categorias_servico {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text nome? filters=trim
    text tipo_itil? filters=trim
    decimal sla_horas?
    text desc? filters=trim
    bool permite_abertura_manual?=false
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "SlpRM3zb744b2w0KqDyVj7bamLI"

  items = [
    {
      id                       : 1
      created_at               : 1787365720183
      nome                     : "Totem Offline / Sem Heartbeat"
      tipo_itil                : "Incidente"
      sla_horas                : 1
      desc                     : "Criada automaticamente quando o ativo fica mais de 5 minutos sem telemetria"
      permite_abertura_manual  : false
    }
    {
      id                       : 2
      created_at               : 1787365761748
      nome                     : "Falha de Rede"
      tipo_itil                : "Incidente"
      sla_horas                : 2
      desc                     : "Totem sem conectividade ou com problema de comunicação"
      permite_abertura_manual  : true
    }
    {
      id                       : 3
      created_at               : 1787365772676
      nome                     : "Tela / Display com Defeito"
      tipo_itil                : "Incidente"
      sla_horas                : 4
      desc                     : "Tela quebrada, apagada ou sem funcionamento"
      permite_abertura_manual  : true
    }
    {
      id                       : 4
      created_at               : 1787365844047
      nome                     : "Periférico com Defeito"
      tipo_itil                : "Incidente"
      sla_horas                : 4
      desc                     : "Leitor, impressora, pinpad ou outro periférico com falha"
      permite_abertura_manual  : true
    }
    {
      id                       : 5
      created_at               : 1787365847000
      nome                     : "Falha de Energia"
      tipo_itil                : "Incidente"
      sla_horas                : 2
      desc                     : "Totem desligado ou sem alimentação elétrica"
      permite_abertura_manual  : true
    }
    {
      id                       : 6
      created_at               : 1787365849303
      nome                     : "Cabo / Conexão Física"
      tipo_itil                : "Incidente"
      sla_horas                : 4
      desc                     : "Cabo desconectado ou conexão física comprometida"
      permite_abertura_manual  : true
    }
    {
      id                       : 7
      created_at               : 1787365951596
      nome                     : "Dano Físico no Totem"
      tipo_itil                : "Incidente"
      sla_horas                : 8
      desc                     : "Estrutura, gabinete ou equipamento fisicamente danificado"
      permite_abertura_manual  : true
    }
    {
      id                       : 8
      created_at               : 1787365953819
      nome                     : "Alta Temperatura"
      tipo_itil                : "Incidente"
      sla_horas                : 2
      desc                     : "Temperatura anormal identificada pela telemetria"
      permite_abertura_manual  : false
    }
    {
      id                       : 9
      created_at               : 1787365955909
      nome                     : "Alto Uso de CPU"
      tipo_itil                : "Incidente"
      sla_horas                : 4
      desc                     : "Uso de CPU acima do comportamento esperado"
      permite_abertura_manual  : false
    }
    {
      id                       : 10
      created_at               : 1787366029201
      nome                     : "Alto Uso de Memória"
      tipo_itil                : "Incidente"
      sla_horas                : 4
      desc                     : "Consumo elevado de memória"
      permite_abertura_manual  : false
    }
    {
      id                       : 11
      created_at               : 1787366031359
      nome                     : "Solicitação de Manutenção"
      tipo_itil                : "Requisição"
      sla_horas                : 24
      desc                     : "Manutenção preventiva ou intervenção sem falha ativa"
      permite_abertura_manual  : true
    }
    {
      id                       : 12
      created_at               : 1787366033971
      nome                     : "Solicitação Operacional"
      tipo_itil                : "Requisição"
      sla_horas                : 24
      desc                     : "Demanda da loja que não caracteriza incidente técnico"
      permite_abertura_manual  : true
    }
  ]
}
