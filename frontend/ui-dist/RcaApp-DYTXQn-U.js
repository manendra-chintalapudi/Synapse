import{c as e,r as s,t as a}from"./jsx-runtime-BqTQeK5L.js";import{A as i,B as r,F as n,H as t,P as c,R as l,U as d,V as o,W as h,a as p,b as u,c as x,d as j,f as m,g as _,h as v,i as f,k as g,l as y,m as b,n as N,o as k,p as w,r as C,s as S,t as z,u as M,v as R,y as A,z as q}from"./ui-BQqDlfse.js";import{n as E,r as L,t as F}from"./wrench-xFo77s5m.js";import{_ as $,a as T,c as I,d as O,f as U,g as H,h as P,i as B,l as D,m as V,n as G,o as Q,p as W,r as J,s as K,t as Y,u as X}from"./dist-C2wCnICZ.js";var Z=r("calendar-days",[["path",{d:"M8 2v4",key:"1cmpym"}],["path",{d:"M16 2v4",key:"4m81vk"}],["rect",{width:"18",height:"18",x:"3",y:"4",rx:"2",key:"1hopcy"}],["path",{d:"M3 10h18",key:"8toen8"}],["path",{d:"M8 14h.01",key:"6423bh"}],["path",{d:"M12 14h.01",key:"1etili"}],["path",{d:"M16 14h.01",key:"1gbofw"}],["path",{d:"M8 18h.01",key:"lrp35t"}],["path",{d:"M12 18h.01",key:"mhygvu"}],["path",{d:"M16 18h.01",key:"kzsmim"}]]),ee=r("file-text",[["path",{d:"M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z",key:"1oefj6"}],["path",{d:"M14 2v5a1 1 0 0 0 1 1h5",key:"wfsgrz"}],["path",{d:"M10 9H8",key:"b1mrlr"}],["path",{d:"M16 13H8",key:"t4e002"}],["path",{d:"M16 17H8",key:"z1uh3a"}]]),se=r("history",[["path",{d:"M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8",key:"1357e3"}],["path",{d:"M3 3v5h5",key:"1xhq8a"}],["path",{d:"M12 7v5l4 2",key:"1fdv2h"}]]),ae=r("list-filter",[["path",{d:"M2 5h20",key:"1fs1ex"}],["path",{d:"M6 12h12",key:"8npq4p"}],["path",{d:"M9 19h6",key:"456am0"}]]),ie=r("octagon-alert",[["path",{d:"M12 16h.01",key:"1drbdi"}],["path",{d:"M12 8v4",key:"1got3b"}],["path",{d:"M15.312 2a2 2 0 0 1 1.414.586l4.688 4.688A2 2 0 0 1 22 8.688v6.624a2 2 0 0 1-.586 1.414l-4.688 4.688a2 2 0 0 1-1.414.586H8.688a2 2 0 0 1-1.414-.586l-4.688-4.688A2 2 0 0 1 2 15.312V8.688a2 2 0 0 1 .586-1.414l4.688-4.688A2 2 0 0 1 8.688 2z",key:"1fd625"}]]),re=r("refresh-cw",[["path",{d:"M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8",key:"v9h5vc"}],["path",{d:"M21 3v5h-5",key:"1q7to0"}],["path",{d:"M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16",key:"3uifl3"}],["path",{d:"M8 16H3v5",key:"1cv678"}]]),ne=r("rotate-ccw",[["path",{d:"M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8",key:"1357e3"}],["path",{d:"M3 3v5h5",key:"1xhq8a"}]]),te=r("test-tube-diagonal",[["path",{d:"M21 7 6.82 21.18a2.83 2.83 0 0 1-3.99-.01a2.83 2.83 0 0 1 0-4L17 3",key:"1ub6xw"}],["path",{d:"m16 2 6 6",key:"1gw87d"}],["path",{d:"M12 16H4",key:"1cjfip"}]]),ce=r("user-round",[["circle",{cx:"12",cy:"8",r:"5",key:"1hypcn"}],["path",{d:"M20 21a8 8 0 0 0-16 0",key:"rfgkzh"}]]),le=r("workflow",[["rect",{width:"8",height:"8",x:"3",y:"3",rx:"2",key:"by2w9f"}],["path",{d:"M7 11v4a2 2 0 0 0 2 2h4",key:"xkn7yn"}],["rect",{width:"8",height:"8",x:"13",y:"13",rx:"2",key:"1cgmvn"}]]),de=/* @__PURE__ */e(s(),1),oe=a(),he={equipmentType:"",dateFrom:"",dateTo:"",severity:"",hasRca:"",sort:"recent"};function pe(e,s="—"){return null==e||""===e?s:String(e)}function ue(e){const s=String(e||"").toLowerCase();return"critical"===s||"high"===s?"red":"medium"===s?"amber":"low"===s?"cyan":"neutral"}function xe(e){const s=String(e||"").toLowerCase();return"resolved"===s?"green":"recurring"===s?"violet":"open"===s?"amber":"neutral"}function je(e){const s=String(e||"").toLowerCase();return"high"===s?"green":"medium"===s?"amber":"red"}function me(e){const s=e?`#/rca/${encodeURIComponent(e)}`:"#/rca";if(window.location.hash!==s)try{window.history.pushState(window.history.state,"",s)}catch{window.location.hash=s.slice(1)}}function _e(e){let s;if("object"==typeof e&&null!==e)try{s=JSON.stringify(e)}catch{s=String(e)}else s=pe(e);return s.length>320?`${s.slice(0,317)}…`:s}function ve({step:e,onClose:s}){const a=(i=e?.record,Array.isArray(i)?i.map(e=>e&&"object"==typeof e?e:{value:e}):i&&"object"==typeof i?[i]:null==i?[]:[{value:i}]);var i;const r=`${pe(e?.kind,"Evidence")} record${a.length>1?"s":""}`,n=document.getElementById("rca-react-root");/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsx)(Y,{open:Boolean(e),onOpenChange:e=>!e&&s(),children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(Q,{container:n,children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(T,{className:"sp-dialog-overlay"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(J,{className:"sp-dialog","aria-describedby":"sp-rca-record-description",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-dialog__head sp-dialog__header",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(K,{className:"sp-dialog__title",children:r}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(B,{className:"sp-dialog__description",id:"sp-rca-record-description",children:e?.id?`${pe(e.kind)} ${pe(e.id)} · direct linked record`:`No linked ${String(e?.kind||"evidence").toLowerCase()} record was found.`})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(G,{asChild:!0,children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(v,{label:"Close record preview",variant:"ghost",size:"icon",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(D,{size:18,"aria-hidden":"true"})})})]}),a.length?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-dialog__records",children:[a.slice(0,6).map((s,i)=>{const r=Object.entries(s).filter(([,e])=>null!==e&&""!==e);/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)("section",{className:"sp-dialog__record",children:[a.length>1&&/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("h3",{children:["Record ",i+1]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dl",{className:"sp-record-grid",children:r.slice(0,12).map(([e,s])=>/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-record sp-record-grid__item",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dt",{children:R(e)}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dd",{children:_e(s)})]},e))})]},`${String(e?.kind)}-${i}`)}),a.length>6&&/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("p",{className:"sp-dialog__more",children:["Showing 6 of ",A(a.length)," linked records."]})]}):/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(x,{title:"Evidence gap",detail:`No ${String(e?.kind||"evidence").toLowerCase()} is linked to this failure in Neo4j.`})]})]})})}function fe({row:e}){/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)("div",{className:"sp-rca-badges",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(z,{tone:ue(e.severity),children:R(e.severity)}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(z,{tone:xe(e.status),children:R(e.status)}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(z,{tone:e.has_rca?"green":"neutral",children:e.has_rca?"RCA linked":"RCA missing"})]})}function ge({rows:e,openFailure:s}){/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsx)("div",{className:"sp-table-scroll sp-rca__table-wrap sp-desktop-only",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("table",{className:"sp-table sp-rca__table",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("caption",{className:"sp-sr-only",children:"Failure records. Select a row to inspect its evidence and RCA."}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("thead",{children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("tr",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("th",{scope:"col",children:"Equipment"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("th",{scope:"col",children:"Failure date"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("th",{scope:"col",children:"Failure mode"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("th",{scope:"col",children:"Severity"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("th",{scope:"col",children:"Status"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("th",{scope:"col",children:"RCA"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("th",{scope:"col",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{className:"sp-sr-only",children:"Open record"})})]})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("tbody",{children:e.map(e=>{const a=()=>s(e.failure_id);/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)("tr",{className:"sp-rca__row",tabIndex:0,"aria-label":`Open failure ${e.failure_id}`,onClick:a,onKeyDown:e=>{"Enter"!==e.key&&" "!==e.key||(e.preventDefault(),a())},children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("td",{className:"sp-table__primary",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("strong",{children:pe(e.equipment_name,"Unknown equipment")}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("small",{children:[pe(e.equipment_id)," · ",R(e.equipment_type)]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("td",{children:u(e.failure_date)}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("td",{className:"sp-table__primary",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("strong",{children:R(e.failure_mode)}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("small",{children:e.recurrence_count>1?`${A(e.recurrence_count)} matching causes`:"No matching recurrence"})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("td",{children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(z,{tone:ue(e.severity),children:R(e.severity)})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("td",{children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(z,{tone:xe(e.status),children:R(e.status)})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("td",{children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("span",{className:e.has_rca?"sp-rca__yes":"sp-rca__no",children:[e.has_rca?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(l,{size:16,"aria-hidden":"true"}):"—",/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{className:"sp-sr-only",children:e.has_rca?"RCA linked":"No RCA"})]})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("td",{children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(N,{variant:"ghost",size:"icon","aria-label":`Open failure ${e.failure_id}`,onClick:e=>{e.stopPropagation(),a()},children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(q,{className:"sp-rca__row-arrow",size:17,"aria-hidden":"true"})})})]},e.failure_id)})})]})})}function ye({rows:e,openFailure:s}){/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsx)("div",{className:"sp-mobile-list sp-rca__mobile-list",children:e.map(e=>/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("button",{className:"sp-mobile-card sp-rca-mobile-card",onClick:()=>s(e.failure_id),children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("span",{className:"sp-rca-mobile-card__topline",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{children:e.failure_id}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{children:u(e.failure_date)})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("strong",{children:pe(e.equipment_name,"Unknown equipment")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("small",{children:[pe(e.equipment_id)," · ",R(e.equipment_type)]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("span",{className:"sp-rca-mobile-card__mode",children:R(e.failure_mode)}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("span",{className:"sp-rca-mobile-card__footer",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(fe,{row:e}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(q,{size:17,"aria-hidden":"true"})]})]},e.failure_id))})}function be({steps:e,onPreview:s}){return e.length?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("div",{className:"sp-rca-chain","aria-label":"Linked evidence chain",children:e.map((a,i)=>{const r=(n=a.kind,{failure:ie,rca:W,technician:ce,procedure:le,deviation:c,standard:O,document:ee}[String(n||"").toLowerCase()]||U);var n;const t=!a.id;/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)(de.Fragment,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("button",{className:"sp-rca-chain__step"+(t?" sp-rca-chain__step--missing":""),onClick:()=>s(a),"aria-label":t?`Inspect missing ${pe(a.kind,"evidence")} link`:`Preview ${pe(a.kind)} ${pe(a.id)}`,children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("span",{className:"sp-rca-chain__icon",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(r,{size:17,"aria-hidden":"true"})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("span",{className:"sp-rca-chain__kind",children:pe(a.kind,"Evidence")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("strong",{children:pe(a.id,"Evidence gap")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("small",{children:pe(a.label,"Not linked")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(z,{tone:"RAG"===a.citation?"violet":"cyan",children:pe(a.citation,"Graph")})]}),i<e.length-1&&/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(q,{className:"sp-rca-chain__connector",size:16,"aria-hidden":"true"})]},`${String(a.kind)}-${i}`)})}):/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(x,{title:"No evidence chain found",detail:"This failure has no graph-linked evidence records."})}function Ne({detail:e}){const s=e.rca||{},a=e.technician||{},i=Array.isArray(e.documents)&&e.documents.length>0;/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)(C,{className:"sp-rca-panel",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(k,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(S,{children:"RCA narrative"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(p,{children:"Recorded finding, response, and procedure gap"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(z,{tone:s.rca_id?"indigo":"neutral",children:pe(s.rca_id,"No RCA")})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(f,{className:"sp-rca-narrative",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("article",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{className:"sp-rca-narrative__icon",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(X,{size:17,"aria-hidden":"true"})}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("h3",{children:"Root-cause finding"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("p",{children:pe(s.root_cause_text,"No root-cause finding is recorded.")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(z,{tone:"cyan",children:"Graph"})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("article",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{className:"sp-rca-narrative__icon",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(F,{size:17,"aria-hidden":"true"})}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("h3",{children:"Corrective action"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("p",{children:pe(s.corrective_action,"No corrective action is recorded.")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-rca-citations",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(z,{tone:"cyan",children:"Graph"}),i&&/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(z,{tone:"violet",children:"RAG"})]})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("article",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{className:"sp-rca-narrative__icon",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(le,{size:17,"aria-hidden":"true"})}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("h3",{children:"Procedure finding"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("p",{children:pe(s.violated_step,"No violated step is recorded.")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(z,{tone:"cyan",children:"Graph"})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-rca-byline",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("span",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(ce,{size:15,"aria-hidden":"true"})," Technician: ",
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("strong",{children:pe(a.name,"Unlinked")}),a.technician_id?` (${a.technician_id})`:""]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("span",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(Z,{size:15,"aria-hidden":"true"})," RCA date: ",
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("strong",{children:u(s.rca_date)})]})]})]})]})}function ke({tests:e}){/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)(C,{className:"sp-rca-panel",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(k,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(S,{children:"Downstream impact"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(p,{children:[A(e.length)," linked quality result",1===e.length?"":"s"]})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(te,{size:19,"aria-hidden":"true"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(f,{children:e.length?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(oe.Fragment,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("div",{className:"sp-rca-impact-wrap",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("table",{className:"sp-rca-impact",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("caption",{className:"sp-sr-only",children:"Quality tests downstream of this failure"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("thead",{children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("tr",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("th",{scope:"col",children:"Test ID"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("th",{scope:"col",children:"Result"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("th",{scope:"col",children:"Standard"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("th",{scope:"col",children:"Test date"})]})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("tbody",{children:e.slice(0,50).map((e,s)=>/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("tr",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("td",{children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("strong",{children:pe(e.test_id)})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("td",{children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(z,{tone:String(e.result||"").toLowerCase().startsWith("fail")?"red":"green",children:pe(e.result)})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("td",{children:pe(e.standard_id)}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("td",{children:u(e.test_date)})]},pe(e.test_id,String(s))))})]})}),e.length>50&&/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("p",{className:"sp-rca-panel__note",children:["Showing 50 of ",A(e.length)," linked results."]})]}):/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(x,{title:"No downstream quality impact linked",detail:"No QualityTest is reachable through this failure’s deviations and coils."})})]})}function we({actions:e,checked:s,setChecked:a}){/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)(C,{className:"sp-rca-panel sp-rca-actions",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(k,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(S,{children:"Recommended action checklist"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(p,{children:"Deterministic actions derived from recorded RCA fields"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(H,{size:19,"aria-hidden":"true"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(f,{children:e.length?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("div",{className:"sp-rca-checklist",children:e.map((e,i)=>/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("label",{className:"sp-rca-checklist__item",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("input",{type:"checkbox",checked:Boolean(s[i]),onChange:e=>a(s=>({...s,[i]:e.target.checked})),"aria-label":`Mark action ${i+1} complete`}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("span",{className:"sp-rca-checklist__check",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(l,{size:14,"aria-hidden":"true"})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("span",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(z,{tone:"indigo",children:pe(e.role,"Owner")}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("p",{children:pe(e.text)})]})]},`${String(e.role)}-${i}`))}):/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(x,{title:"No role-scoped action available",detail:"No action can be derived from the recorded RCA fields."})})]})}function Ce({detail:e,openFailure:s}){const a=e.recurrences||[];/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)(C,{className:"sp-rca-panel sp-rca-sidebar-card",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(k,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(S,{children:"Recurrence"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(p,{children:"Exact normalized cause or action"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(se,{size:18,"aria-hidden":"true"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(f,{children:e.recurrence_count?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(oe.Fragment,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-rca-recurrence__callout",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("strong",{children:A(e.recurrence_count)}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("span",{children:["other failure",1===e.recurrence_count?"":"s"," share this cause or corrective action"]})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-rca-recurrence__links",children:[a.slice(0,12).map(e=>/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("button",{onClick:()=>s(String(e.failure_id)),children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("span",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("strong",{children:pe(e.failure_id)}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("small",{children:R(e.failure_mode)})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(q,{size:15,"aria-hidden":"true"})]},pe(e.failure_id))),e.recurrence_count>12&&/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("small",{children:["+",A(e.recurrence_count-12)," more linked failures"]})]})]}):/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(x,{title:"No matching recurrence",detail:"No other RCA has the same normalized root-cause text or corrective action."})})]})}function Se({detail:e}){const s=e.confidence||{};/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)(C,{className:"sp-rca-panel sp-rca-sidebar-card",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(k,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(S,{children:"Confidence"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(p,{children:"Evidence-calibrated, no model self-scoring"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(n,{size:18,"aria-hidden":"true"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(f,{className:"sp-rca-confidence",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(z,{tone:je(s.level),children:R(s.level||"low")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("p",{children:pe(s.reason,"No confidence evidence is recorded.")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("dl",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dt",{children:"Sample size"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dd",{children:A(s.sample_size||1)})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dt",{children:"Source types"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dd",{children:A(s.corroborating_sources||0)})]})]})]})]})}function ze({detail:e}){const s=e.provenance||{};/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)(C,{className:"sp-rca-panel sp-rca-sidebar-card",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(k,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(S,{children:"Provenance"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(p,{children:"How this view was assembled"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(V,{size:18,"aria-hidden":"true"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(f,{className:"sp-rca-provenance",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(b,{children:"Direct Neo4j · no LLM"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("dl",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dt",{children:"Query mode"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dd",{children:R(s.query_mode||"direct_read_only_cypher")})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dt",{children:"LLM used"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dd",{children:s.llm_used?"Yes":"No"})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("p",{children:pe(s.procedure_path,"Procedure link unavailable")})]})]})}function Me({detail:e,failureId:s,loading:a,error:i,retry:r,goBack:n,openFailure:c}){const[l,x]=de.useState(null),[j,m]=de.useState({}),_=de.useRef(null);if(de.useEffect(()=>{const e=()=>{"rca"!==window.location.hash.replace(/^#\//,"").split("/")[0]&&x(null)};return window.addEventListener("hashchange",e),window.addEventListener("popstate",e),()=>{window.removeEventListener("hashchange",e),window.removeEventListener("popstate",e)}},[]),de.useEffect(()=>{x(null),m({})},[s]),de.useEffect(()=>{e&&_.current?.focus()},[e]),a&&!e)/* @__PURE__ */ /* @__PURE__ */return(0,oe.jsxs)("div",{className:"sp-rca-detail",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(N,{variant:"ghost",onClick:n,children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(E,{size:16,"aria-hidden":"true"})," All failures"]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(M,{label:`Loading ${s} evidence…`})]});if(i||!e)/* @__PURE__ */ /* @__PURE__ */return(0,oe.jsxs)("div",{className:"sp-rca-detail",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(N,{variant:"ghost",onClick:n,children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(E,{size:16,"aria-hidden":"true"})," All failures"]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(y,{error:i||`Failure ${s} was not found.`,retry:r})]});const v=e.failure||{},g=e.equipment||{},b={severity:e.severity,status:e.status,has_rca:Boolean(e.rca?.rca_id)};/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)("div",{className:"sp-rca-detail",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("header",{className:"sp-detail-header sp-rca-detail__header",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)(N,{variant:"ghost",onClick:n,children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(E,{size:16,"aria-hidden":"true"})," All failures"]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-detail-header__title sp-rca-detail__identity",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("span",{className:"sp-eyebrow",children:["Failure evidence · ",pe(v.failure_id,s)]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("h1",{ref:_,tabIndex:-1,children:pe(g.name||g.equipment_id,"Unknown equipment")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("p",{children:[pe(g.equipment_id)," · ",u(v.timestamp)," · ",R(v.failure_mode)]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("div",{className:"sp-detail-header__badges",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(fe,{row:b})})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)(C,{className:"sp-rca-panel sp-rca-evidence-card",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(k,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(S,{children:"Evidence chain"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(p,{children:"Focused graph trail · select any step to preview its record"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(U,{size:19,"aria-hidden":"true"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(f,{children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(be,{steps:e.evidence_chain||[],onPreview:x})})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-detail-grid sp-rca-detail__grid",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(d,{className:"sp-tabs sp-stack sp-rca-detail__main",defaultValue:"analysis",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)(t,{className:"sp-tabs__list","aria-label":"Failure detail sections",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)(h,{className:"sp-tabs__trigger",value:"analysis",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(W,{size:15,"aria-hidden":"true"})," Analysis"]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)(h,{className:"sp-tabs__trigger",value:"impact",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(te,{size:15,"aria-hidden":"true"})," Downstream impact ",
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("span",{children:A(e.downstream_tests?.length||0)})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)(h,{className:"sp-tabs__trigger",value:"actions",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(H,{size:15,"aria-hidden":"true"})," Actions ",
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("span",{children:A(e.recommended_actions?.length||0)})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(o,{className:"sp-tabs__content",value:"analysis",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(Ne,{detail:e})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(o,{className:"sp-tabs__content",value:"impact",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(ke,{tests:e.downstream_tests||[]})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(o,{className:"sp-tabs__content",value:"actions",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(we,{actions:e.recommended_actions||[],checked:j,setChecked:m})})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("aside",{className:"sp-stack sp-rca-detail__sidebar",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(Ce,{detail:e,openFailure:c}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(Se,{detail:e}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(ze,{detail:e})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(ve,{step:l,onClose:()=>x(null)})]})}function Re({initialFailureId:e}){const[s,a]=de.useState(null),[r,n]=de.useState(!0),[t,c]=de.useState(""),[l,d]=de.useState(0),[o,h]=de.useState(he),[u,N]=de.useState(null),[q,E]=de.useState(!0),[F,T]=de.useState(""),[O,U]=de.useState(0),[H,B]=de.useState(e||null),[D,V]=de.useState(null),[G,Q]=de.useState(Boolean(e)),[W,J]=de.useState(""),[K,Y]=de.useState(0),X=de.useCallback(e=>{const s=String(e||"").trim();s&&(B(s),V(null),J(""),me(s))},[]),ee=de.useCallback(()=>{B(null),V(null),J(""),me()},[]);de.useEffect(()=>{let e=!0;return n(!0),c(""),_("/api/rca/summary").then(s=>e&&a(s)).catch(s=>e&&c(s instanceof Error?s.message:String(s))).finally(()=>e&&n(!1)),()=>{e=!1}},[l]),de.useEffect(()=>{let e=!0;const s=new URLSearchParams;return o.equipmentType&&s.set("equipment_type",o.equipmentType),o.dateFrom&&s.set("date_from",o.dateFrom),o.dateTo&&s.set("date_to",o.dateTo),o.severity&&s.set("severity",o.severity),o.hasRca&&s.set("has_rca",o.hasRca),s.set("sort",o.sort||"recent"),E(!0),T(""),_(`/api/rca/failures?${s.toString()}`).then(s=>e&&N(s)).catch(s=>e&&T(s instanceof Error?s.message:String(s))).finally(()=>e&&E(!1)),()=>{e=!1}},[o,O]),de.useEffect(()=>{if(!H)return;let e=!0;return Q(!0),J(""),_(`/api/rca/failures/${encodeURIComponent(H)}`).then(s=>e&&V(s)).catch(s=>e&&J(s instanceof Error?s.message:String(s))).finally(()=>e&&Q(!1)),()=>{e=!1}},[H,K]),de.useEffect(()=>{e&&X(e)},[e,X]),de.useEffect(()=>{const e=e=>{const s=e.detail;let a="";if("string"==typeof s)a=s;else if(s&&"object"==typeof s){const e=s;a=String(e.failureId||e.failure_id||"")}a&&X(a)};return window.addEventListener("synapse-open-failure",e),()=>window.removeEventListener("synapse-open-failure",e)},[X]),de.useEffect(()=>{const e=()=>{const e=function(){const e=window.location.hash.replace(/^#\//,"").split("/");if("rca"!==e[0]||!e[1])return"";try{return decodeURIComponent(e.slice(1).join("/"))}catch{return e.slice(1).join("/")}}();B(e||null),e||(V(null),J(""))};return window.addEventListener("popstate",e),window.addEventListener("hashchange",e),()=>{window.removeEventListener("popstate",e),window.removeEventListener("hashchange",e)}},[]);const se=u?.failures||[],ie=(e,s)=>{h(a=>({...a,[e]:s}))};/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsx)("section",{className:"sp-rca","aria-label":"RCA and failures",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(i,{mode:"wait",initial:!1,children:H?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(g.div,{className:"sp-rca__view",initial:{opacity:0,x:18},animate:{opacity:1,x:0},exit:{opacity:0,x:12},transition:{duration:.2,ease:"easeOut"},children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(Me,{detail:D,failureId:H,loading:G,error:W,retry:()=>Y(e=>e+1),goBack:ee,openFailure:X})},`detail-${H}`):/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(g.div,{className:"sp-rca__view",initial:{opacity:0,x:-12},animate:{opacity:1,x:0},exit:{opacity:0,x:-12},transition:{duration:.2,ease:"easeOut"},children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(m,{eyebrow:"RCA & Failures",title:"Failure intelligence, fully traceable",description:"Move from an equipment event to its evidence, root cause, downstream impact, and response without losing the thread.",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(b,{children:"Direct Neo4j · no LLM"})}),r&&!s?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(M,{label:"Loading failure overview…"}):t&&!s?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(y,{error:t,retry:()=>d(e=>e+1)}):s?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("section",{className:"sp-metrics sp-rca__metrics","aria-label":"RCA summary",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(j,{icon:L,index:0,label:"Total failures",value:A(s.total_failures),detail:"Tracked equipment events"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(j,{icon:$,index:1,label:"RCA completion",value:`${Number(s.rca_completion_pct||0).toFixed(1)}%`,detail:`${A(s.failures_with_rca)} completed records`,featured:!0}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(j,{icon:I,index:2,label:"Most common mode",value:A(s.most_common_failure_mode?.count),detail:R(s.most_common_failure_mode?.name)}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(j,{icon:P,index:3,label:"Most affected equipment",value:A(s.most_affected_equipment?.count),detail:s.most_affected_equipment?.name||s.most_affected_equipment?.equipment_id||"—"})]}):null,
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)(C,{className:"sp-rca__browser",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(k,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(S,{children:"Failure register"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(p,{children:"Filter the operating history, then select a failure to follow its evidence."})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-rca__browser-actions",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(z,{tone:"indigo",children:q?"Updating…":`${A(u?.count||0)} failures`}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(v,{label:"Clear all filters",variant:"ghost",size:"icon",onClick:()=>h(he),disabled:Object.entries(o).every(([e,s])=>s===("sort"===e?"recent":"")),children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(ne,{size:16,"aria-hidden":"true"})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(v,{label:"Refresh failure records",variant:"ghost",size:"icon",onClick:()=>U(e=>e+1),children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(re,{size:16,"aria-hidden":"true"})})]})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(f,{children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-rca__filter-heading",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(ae,{size:16,"aria-hidden":"true"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{children:"Six ways to focus the register"})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-fields sp-rca__filters",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(w,{label:"Equipment type",value:o.equipmentType,onValueChange:e=>ie("equipmentType",e),placeholder:"All equipment",options:(s?.filters.equipment_types||[]).map(e=>({value:e,label:R(e)}))}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("label",{className:"sp-field",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{children:"From date"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("span",{className:"sp-date-input",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(Z,{size:15,"aria-hidden":"true"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("input",{type:"date",value:o.dateFrom,min:s?.filters.date_min||void 0,max:s?.filters.date_max||void 0,onChange:e=>ie("dateFrom",e.target.value)})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("label",{className:"sp-field",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{children:"To date"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("span",{className:"sp-date-input",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(Z,{size:15,"aria-hidden":"true"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("input",{type:"date",value:o.dateTo,min:s?.filters.date_min||void 0,max:s?.filters.date_max||void 0,onChange:e=>ie("dateTo",e.target.value)})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(w,{label:"Severity",value:o.severity,onValueChange:e=>ie("severity",e),placeholder:"All severities",options:(s?.filters.severities||[]).map(e=>({value:e,label:R(e)}))}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(w,{label:"RCA coverage",value:o.hasRca,onValueChange:e=>ie("hasRca",e),placeholder:"All RCA states",options:[{value:"true",label:"RCA completed"},{value:"false",label:"RCA missing"}]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(w,{label:"Sort by",value:o.sort,onValueChange:e=>ie("sort",e||"recent"),options:[{value:"recent",label:"Most recent"},{value:"severe",label:"Highest severity"},{value:"recurring",label:"Most recurring"}]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("div",{className:"sp-rca__results","aria-live":"polite","aria-busy":q,children:q?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(M,{label:"Loading failure records…"}):F?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(y,{error:F,retry:()=>U(e=>e+1)}):se.length?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(oe.Fragment,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(ge,{rows:se,openFailure:X}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(ye,{rows:se,openFailure:X})]}):/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(x,{title:"No matching failures",detail:"Try widening the date range or clearing one of the filters."})})]})]})]},"failure-list")})})}export{Re as default};