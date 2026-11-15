// Reconfere o plano inteiro e cria no máximo um par por execução operacional.
function "demonstracao/gravar_etapa" {
  input {
    text data_base
    int ativos_referencia_id
    int indice
  }
  stack {
    function.run "demonstracao/planejar_confiabilidade" {
      input = {data_base: $input.data_base}
    } as $previa
    api.lambda {
      code = """
        const e=$var.previa.plano.etapas.find(x=>x.ativo_id===$input.ativos_referencia_id&&x.indice===$input.indice);
        if(!e)throw new Error('Etapa fora do plano autorizado.');
        return e;
        """
      timeout = 10
    } as $etapa
    var $fatos { value = [] }
    foreach ($etapa.amostras) {
      each as $a {
        function.run "demonstracao/garantir_fato" {
          input = {ativos_referencia_id: $etapa.ativo_id, tipo: "telemetria", dados: $a}
        } as $amostra
        array.push $fatos { value = $amostra }
      }
    }
    foreach ($etapa.eventos) {
      each as $e {
        db.query telemetria_equipamentos {
          where = $db.telemetria_equipamentos.ativos_referencia_id == $etapa.ativo_id && $db.telemetria_equipamentos.evento_timestamp == $e.referencia_timestamp
          return = {type: "single"}
        } as $referencia
        precondition ($referencia != null) {
          error_type = "inputerror"
          error = "Referência de telemetria ausente."
        }
        function.run "demonstracao/garantir_fato" {
          input = {ativos_referencia_id: $etapa.ativo_id, tipo: "transicao", dados: {ativos_referencia_id: $etapa.ativo_id, status: $e.status, detectado_em: $e.detectado_em, telemetria_referencia_id: $referencia.id, heartbeat_limite_minutos: 15}}
        } as $evento
        array.push $fatos { value = $evento }
      }
    }
  }
  response = {ativo_id: $etapa.ativo_id, indice: $etapa.indice, fatos: $fatos}
  guid = "miraDemoGravarEtapa02"
}
