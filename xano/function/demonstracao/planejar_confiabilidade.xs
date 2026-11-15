// Prévia sem escrita: plano fechado nos Totens EXISTENTES 1 e 2.
function "demonstracao/planejar_confiabilidade" {
  input { text data_base }
  stack {
    var $agora { value = now }
    db.query ativos_referencia { return = {type: "count"} } as $c0
    db.query categorias_servico { return = {type: "count"} } as $c1
    db.query chamados { return = {type: "count"} } as $c2
    db.query historico_disponibilidade_totens { return = {type: "count"} } as $c3
    db.query historico_vinculos_totem_loja { return = {type: "count"} } as $c4
    db.query interacoes_chamado { return = {type: "count"} } as $c5
    db.query lojas { return = {type: "count"} } as $c6
    db.query preferencias_fila_chamados { return = {type: "count"} } as $c7
    db.query telemetria_equipamentos { return = {type: "count"} } as $c8
    db.query usuarios { return = {type: "count"} } as $c9
    var $ocupacao { value = $c0 + $c1 + $c2 + $c3 + $c4 + $c5 + $c6 + $c7 + $c8 + $c9 }
    db.query ativos_referencia {
      where = $db.ativos_referencia.id == 1 || $db.ativos_referencia.id == 2
      return = {type: "list"}
    } as $ativos
    db.query telemetria_equipamentos {
      where = $db.telemetria_equipamentos.ativos_referencia_id == 1 || $db.telemetria_equipamentos.ativos_referencia_id == 2
      return = {type: "list"}
    } as $telemetrias
    db.query historico_disponibilidade_totens {
      where = $db.historico_disponibilidade_totens.ativos_referencia_id == 1 || $db.historico_disponibilidade_totens.ativos_referencia_id == 2
      return = {type: "list"}
    } as $eventos
    api.lambda {
      code = """
        const base=$input.data_base,t0=Date.parse(base+'T00:00:00-03:00')-30*86400000,t1=t0+30*86400000;
        if(base!=='2026-11-14'||t0<1791169200000||t1>$var.agora) throw new Error('Data fora do plano autorizado.');
        const ativos=[1,2].map((id,k)=>{
          const rows=$var.ativos.filter(x=>x.id===id),nome='TOT-PAU-00'+id;
          if(rows.length!==1||rows[0].nome_ativo!==nome||rows[0].lojas_id!==1||rows[0].tipo!=='Totem')
            throw new Error('Cadastro existente divergiu; não criar substitutos.');
          return {id,nome,loja_id:1};
        });
        const am=(id,t,cpu=35,mem=44,temp=45)=>({ativos_referencia_id:id,evento_timestamp:t,uso_cpu:cpu,uso_memoria:mem,temperatura:temp,status_rede:'online'});
        const etapas=ativos.flatMap((a,k)=>[{ativo_id:a.id,indice:-1,amostras:[am(a.id,t0)],eventos:[]},
          ...Array.from({length:30},(_,n)=>{
            const b=t0+n*86400000+(5+k)*3600000,last=b+((n+k*2)%5)*60000;
            const det=b+20*60000,rec=last+(30+((n*23+k*47)%151))*60000,on=Math.ceil(rec/300000)*300000;
            return {ativo_id:a.id,indice:n,amostras:[am(a.id,last,30+n%20,45+n%15,42+n%10),am(a.id,rec,28+n%18,40+n%20,40+n%12)],
              eventos:[{ativos_referencia_id:a.id,status:'offline',detectado_em:det,referencia_timestamp:last,heartbeat_limite_minutos:15},
                {ativos_referencia_id:a.id,status:'online',detectado_em:on,referencia_timestamp:rec,heartbeat_limite_minutos:15}]};
          })]);
        const ta=etapas.flatMap(e=>e.amostras),ev=etapas.flatMap(e=>e.eventos),te=$var.telemetrias,ee=$var.eventos;
        let existentes=0;
        const iguais=(row,d)=>Object.entries(d).every(([k,v])=>row[k]===v);
        const idsTe=new Set(),idsEv=new Set();
        for(const a of ta){
          const rows=te.filter(x=>x.ativos_referencia_id===a.ativos_referencia_id&&x.evento_timestamp===a.evento_timestamp);
          if(rows.length>1||rows.some(x=>!iguais(x,a)))throw new Error('Telemetria duplicada ou divergente no lote.');
          if(rows.length){existentes++;idsTe.add(rows[0].id);}
        }
        for(const e of ev){
          const rows=ee.filter(x=>x.ativos_referencia_id===e.ativos_referencia_id&&x.detectado_em===e.detectado_em&&x.status===e.status);
          const {referencia_timestamp,...dados}=e;
          if(rows.length>1||rows.some(x=>!iguais(x,dados)||!te.some(t=>t.id===x.telemetria_referencia_id&&t.ativos_referencia_id===e.ativos_referencia_id&&t.evento_timestamp===referencia_timestamp)))
            throw new Error('Transição duplicada ou divergente no lote.');
          if(rows.length){existentes++;idsEv.add(rows[0].id);}
        }
        for(const e of etapas.filter(x=>x.indice>=0)){
          const last=e.amostras[0].evento_timestamp,on=e.eventos[1].detectado_em,id=e.ativo_id;
          const externos=ee.filter(x=>x.ativos_referencia_id===id&&!idsEv.has(x.id));
          const ant=externos.filter(x=>x.detectado_em<=last).sort((a,b)=>b.detectado_em-a.detectado_em)[0];
          if(ant?.status!=='online'||externos.some(x=>x.detectado_em>last&&x.detectado_em<=on)
            ||te.some(x=>x.ativos_referencia_id===id&&!idsTe.has(x.id)&&x.evento_timestamp>last&&x.evento_timestamp<=on))
            throw new Error('Janela histórica ocupada por fatos existentes.');
        }
        if($var.ocupacao+242-existentes>100000)throw new Error('Capacidade insuficiente; nenhuma limpeza automática.');
        return {plano:{versao:2,lote:'DEMO-CONFIABILIDADE-V2-'+base,data_base:base,t0,t1,ativos,etapas,
          contagens:{telemetrias:122,transicoes:120,total:242}},registros_atuais:$var.ocupacao,existentes,faltantes:242-existentes,
          concluidas:etapas.filter(e=>e.amostras.every(a=>te.some(t=>idsTe.has(t.id)&&t.ativos_referencia_id===e.ativo_id&&t.evento_timestamp===a.evento_timestamp))
            &&e.eventos.every(v=>ee.some(x=>idsEv.has(x.id)&&x.ativos_referencia_id===e.ativo_id&&x.detectado_em===v.detectado_em&&x.status===v.status))).map(e=>e.ativo_id+'/'+e.indice)};
        """
      timeout = 10
    } as $resultado
  }
  response = $resultado
  guid = "miraDemoPlanejarConfiabilidade02"
}
