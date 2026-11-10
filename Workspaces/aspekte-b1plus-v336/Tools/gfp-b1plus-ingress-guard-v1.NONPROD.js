/* Gate05 POC ONLY. No app release/promotion; parser must call this BEFORE compaction or durable mutation. */
(function (root) {
  'use strict';
  const VERSION = 'B1PLUS_INGRESS_GUARD_POC_20261110';
  const txt = v => String(v == null ? '' : v).trim();
  const normal = row => ({
    text: txt(row?.text ?? row?.text_de ?? row?.de),
    lang: txt(row?.lang || 'de-DE'),
    translations: Object.entries(Array.isArray(row?.translations)
      ? row.translations.reduce((o, e) => {if (e && e.lang && e.text) (o[e.lang] ||= []).push(e.text);return o;}, {})
      : (row?.translations && typeof row.translations === 'object' ? row.translations : {fa: row?.fa, en:row?.en}))
      .flatMap(([lang, v]) => (Array.isArray(v) ? v : [v]).filter(Boolean).map(text => [lang === 'fa' ? 'fa-IR' : lang === 'en' ? 'en-US' : lang, txt(text)]))
      .sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b)))
  });
  function assess(cards, {allowQaOnly=false}={}) {
    const problems = [], stats={cards:0,rich:0,canonical:0,multiSense:0,networks:0};
    const bad=(code,cardId,exId='',details='')=>problems.push({code,card_id:String(cardId||''),example_id:String(exId||''),details:String(details||'')});
    const cardIds=new Set();
    for(const card of (cards||[])){
      stats.cards++;
      const id=txt(card?.id);
      if(!id||cardIds.has(id))bad('DUPLICATE_OR_EMPTY_CARD_ID',id);
      cardIds.add(id);
      const cf=card?.customFields||{};
      const marked=cf.b1plus_release_gate!=null||cf.b1plus_curated_record_v1!=null;
      if(marked&&!allowQaOnly){
        if(cf.b1plus_release_gate!=='APPROVED_IMPORT'||cf.gfp_production_authorized!==true)
          bad('B1PLUS_NONIMPORT_RELEASE_FENCE',id,'','Curated learner preview must not be imported');
      }
      const networks=Array.isArray(cf.b1plus_sense_network_v1)?cf.b1plus_sense_network_v1:[];
      stats.networks+=networks.length;
      const known=new Set(),dupes=new Set();
      for(const n of networks){let s=txt(n?.sense_id);if(!s||known.has(s))dupes.add(s);known.add(s);}
      for(const d of dupes)bad('DUPLICATE_OR_EMPTY_NETWORK_SENSE',id,'',d);
      const rich=Array.isArray(cf.presentation_examples)?cf.presentation_examples:[];
      const canon=(Array.isArray(cf.canonical_unit?.examples)?cf.canonical_unit.examples:
        Array.isArray(cf.canonical_examples)?cf.canonical_examples:[]);
      stats.rich+=rich.length; stats.canonical+=canon.length;
      function scan(list,kind){
        const byId=new Map();
        for(const e of list){
          const eid=txt(e?.id??e?.example_id),norm=normal(e);
          if(!eid){if(marked)bad('B1PLUS_EXAMPLE_ID_REQUIRED',id,'',kind);continue;}
          if(byId.has(eid))bad('DUPLICATE_SOURCE_EXAMPLE_ID',id,eid,kind);
          byId.set(eid,e);
          if(!norm.text)bad('EMPTY_SOURCE_EXAMPLE_TEXT',id,eid,kind);
          const scalar=txt(e?.sense_id),hasPlural=Object.hasOwn(e,'sense_ids'),arr=e?.sense_ids;
          if(hasPlural){
            if(!Array.isArray(arr)||arr.length===0||arr.some(x=>!txt(x))){bad('MALFORMED_MULTISENSE_ARRAY',id,eid,kind);continue;}
            const a=arr.map(txt);if(new Set(a).size!==a.length)bad('DUPLICATE_MULTISENSE_ID',id,eid,kind);
            if(scalar&&!a.includes(scalar))bad('PRIMARY_SENSE_NOT_IN_MULTISENSE',id,eid,kind);
            for(const sid of a)if(networks.length&&!known.has(sid))bad('ORPHAN_MULTISENSE_LINK',id,eid,sid);
            if(a.length>1)stats.multiSense++;
          } else if(scalar&&networks.length&&!known.has(scalar))bad('ORPHAN_SCALAR_SENSE_LINK',id,eid,scalar);
        }
        return byId;
      }
      const r=scan(rich,'rich'),c=scan(canon,'canonical');
      for(const [eid,e] of c){
        const other=r.get(eid);if(!other)continue;
        if(JSON.stringify(normal(e))!==JSON.stringify(normal(other)))bad('CANONICAL_RICH_SAME_ID_DIFFERENT_CONTENT',id,eid);
        const a=txt(e?.sense_id),b=txt(other?.sense_id);
        if(a&&b&&a!==b)bad('CANONICAL_RICH_PRIMARY_SENSE_CONFLICT',id,eid);
        if(Array.isArray(e?.sense_ids)&&Array.isArray(other?.sense_ids)){
          const arr1=e.sense_ids.map(txt).sort(),arr2=other.sense_ids.map(txt).sort();
          if(JSON.stringify(arr1)!==JSON.stringify(arr2))bad('CANONICAL_RICH_MULTISENSE_CONFLICT',id,eid);
        }
      }
    }
    return {schema:VERSION,ok:problems.length===0,problem_count:problems.length,stats,problems};
  }
  function assertBeforeImport(cards,options){const r=assess(cards,options);if(!r.ok){let ex=r.problems.slice(0,3).map(x=>x.code+':'+x.card_id+':'+x.example_id).join(' | ');throw new Error('B1+ import guard blocked '+r.problem_count+' issue(s): '+ex);}return r;}
  function assessRawTsvBeforeParse(text,parseTsvRows,{allowQaOnly=false}={}) {
    if(typeof parseTsvRows!=='function')throw new Error('Raw TSV guard requires the exact native parseTsv row parser');
    const rows=parseTsvRows(text),issues=[];
    if(!rows.length)return {schema:VERSION,ok:true,problem_count:0,problems:[],stats:{rows:0,qa_cards:0}};
    const headers=rows[0].values.map(x=>txt(x)),customIndex=headers.indexOf('custom_fields'),idIndex=headers.indexOf('id');
    if(customIndex<0)return {schema:VERSION,ok:true,problem_count:0,problems:[],stats:{rows:rows.length-1,qa_cards:0},skipped:'NON_CUSTOM_FIELDS_PROFILE'};
    const cards=[];
    rows.slice(1).forEach((row,i)=>{
      if(row.values.length!==headers.length){issues.push({code:'RAW_TSV_INVALID_COLUMN_COUNT',card_id:txt(row.values[idIndex]),example_id:'',details:'row '+(i+2)});return;}
      let cf={};const val=row.values[customIndex];
      if(val){try{cf=JSON.parse(val)}catch(e){issues.push({code:'RAW_TSV_CUSTOM_FIELDS_JSON_MALFORMED',card_id:txt(row.values[idIndex]),example_id:'',details:'row '+(i+2)});return;}}
      if(!cf||typeof cf!=='object'||Array.isArray(cf)){issues.push({code:'RAW_TSV_CUSTOM_FIELDS_NOT_OBJECT',card_id:txt(row.values[idIndex]),example_id:'',details:'row '+(i+2)});return;}
      if(cf.b1plus_release_gate!=null||cf.b1plus_curated_record_v1!=null||Array.isArray(cf.presentation_examples))
        cards.push({id:idIndex<0?'':txt(row.values[idIndex]),customFields:cf});
    });
    const evaluated=assess(cards,{allowQaOnly});const problems=[...issues,...evaluated.problems];
    return {schema:VERSION,ok:problems.length===0,problem_count:problems.length,problems,
      stats:{raw_tsv_rows:rows.length-1,checked_custom_fields:cards.length,...evaluated.stats}};
  }
  function assertRawTsvBeforeParse(text,parseRows,options){const r=assessRawTsvBeforeParse(text,parseRows,options);if(!r.ok){const e=r.problems.slice(0,3).map(x=>x.code+':'+x.card_id+':'+x.example_id).join(' | ');throw new Error('B1+ RAW TSV ingress blocked '+r.problem_count+' issue(s): '+e);}return r;}
  root.GFP_B1PLUS_IMPORT_GUARD_V1=Object.freeze({assess,assertBeforeImport,assessRawTsvBeforeParse,assertRawTsvBeforeParse,version:VERSION});
})(typeof window!=='undefined'?window:globalThis);