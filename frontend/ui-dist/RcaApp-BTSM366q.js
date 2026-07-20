import{c as e,r as s,t as a}from"./jsx-runtime-BqTQeK5L.js";import{A as i,G as r,V as n,W as t,a as c,b as l,c as d,d as o,f as h,g as p,h as u,i as x,l as j,m,n as _,o as v,p as f,r as g,s as y,t as b,u as N,x as k,y as w}from"./ui-B61WkjWT.js";import{a as C,i as S,n as z,o as A,r as M,s as R,t as q}from"./AnimatePresence-DE55Gjn3.js";import{n as E,r as L,t as F}from"./wrench-Brzo9Ing.js";import{a as $,i as T,n as I,r as O,t as P}from"./sparkles-C1ZyXJN8.js";import{a as U,c as D,d as H,f as V,i as B,l as G,n as Q,o as W,r as J,s as K,t as Y,u as X}from"./dist-JNOywbF1.js";import{t as Z}from"./rotate-ccw-BZLzTzUS.js";var ee=r("calendar-days",[["path",{d:"M8 2v4",key:"1cmpym"}],["path",{d:"M16 2v4",key:"4m81vk"}],["rect",{width:"18",height:"18",x:"3",y:"4",rx:"2",key:"1hopcy"}],["path",{d:"M3 10h18",key:"8toen8"}],["path",{d:"M8 14h.01",key:"6423bh"}],["path",{d:"M12 14h.01",key:"1etili"}],["path",{d:"M16 14h.01",key:"1gbofw"}],["path",{d:"M8 18h.01",key:"lrp35t"}],["path",{d:"M12 18h.01",key:"mhygvu"}],["path",{d:"M16 18h.01",key:"kzsmim"}]]),se=r("file-text",[["path",{d:"M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z",key:"1oefj6"}],["path",{d:"M14 2v5a1 1 0 0 0 1 1h5",key:"wfsgrz"}],["path",{d:"M10 9H8",key:"b1mrlr"}],["path",{d:"M16 13H8",key:"t4e002"}],["path",{d:"M16 17H8",key:"z1uh3a"}]]),ae=r("history",[["path",{d:"M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8",key:"1357e3"}],["path",{d:"M3 3v5h5",key:"1xhq8a"}],["path",{d:"M12 7v5l4 2",key:"1fdv2h"}]]),ie=r("list-filter",[["path",{d:"M2 5h20",key:"1fs1ex"}],["path",{d:"M6 12h12",key:"8npq4p"}],["path",{d:"M9 19h6",key:"456am0"}]]),re=r("octagon-alert",[["path",{d:"M12 16h.01",key:"1drbdi"}],["path",{d:"M12 8v4",key:"1got3b"}],["path",{d:"M15.312 2a2 2 0 0 1 1.414.586l4.688 4.688A2 2 0 0 1 22 8.688v6.624a2 2 0 0 1-.586 1.414l-4.688 4.688a2 2 0 0 1-1.414.586H8.688a2 2 0 0 1-1.414-.586l-4.688-4.688A2 2 0 0 1 2 15.312V8.688a2 2 0 0 1 .586-1.414l4.688-4.688A2 2 0 0 1 8.688 2z",key:"1fd625"}]]),ne=r("refresh-cw",[["path",{d:"M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8",key:"v9h5vc"}],["path",{d:"M21 3v5h-5",key:"1q7to0"}],["path",{d:"M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16",key:"3uifl3"}],["path",{d:"M8 16H3v5",key:"1cv678"}]]),te=r("test-tube-diagonal",[["path",{d:"M21 7 6.82 21.18a2.83 2.83 0 0 1-3.99-.01a2.83 2.83 0 0 1 0-4L17 3",key:"1ub6xw"}],["path",{d:"m16 2 6 6",key:"1gw87d"}],["path",{d:"M12 16H4",key:"1cjfip"}]]),ce=r("user-round",[["circle",{cx:"12",cy:"8",r:"5",key:"1hypcn"}],["path",{d:"M20 21a8 8 0 0 0-16 0",key:"rfgkzh"}]]),le=r("workflow",[["rect",{width:"8",height:"8",x:"3",y:"3",rx:"2",key:"by2w9f"}],["path",{d:"M7 11v4a2 2 0 0 0 2 2h4",key:"xkn7yn"}],["rect",{width:"8",height:"8",x:"13",y:"13",rx:"2",key:"1cgmvn"}]]),de=/* @__PURE__ */e(s(),1),oe=a(),he={equipmentType:"",dateFrom:"",dateTo:"",severity:"",hasRca:"",sort:"recent"};function pe(e,s="—"){return null==e||""===e?s:String(e)}function ue(e){const s=String(e||"").toLowerCase();return"critical"===s||"high"===s?"red":"medium"===s?"amber":"low"===s?"cyan":"neutral"}function xe(e){const s=String(e||"").toLowerCase();return"resolved"===s?"green":"recurring"===s?"violet":"open"===s?"amber":"neutral"}function je(e){const s=String(e||"").toLowerCase();return"high"===s?"green":"medium"===s?"amber":"red"}function me(e){const s=e?`#/rca/${encodeURIComponent(e)}`:"#/rca";if(window.location.hash!==s)try{window.history.pushState(window.history.state,"",s)}catch{window.location.hash=s.slice(1)}}function _e(e){let s;if("object"==typeof e&&null!==e)try{s=JSON.stringify(e)}catch{s=String(e)}else s=pe(e);return s.length>320?`${s.slice(0,317)}…`:s}function ve({step:e,onClose:s}){const a=(i=e?.record,Array.isArray(i)?i.map(e=>e&&"object"==typeof e?e:{value:e}):i&&"object"==typeof i?[i]:null==i?[]:[{value:i}]);var i;const r=`${pe(e?.kind,"Evidence")} record${a.length>1?"s":""}`,n=document.getElementById("rca-react-root");/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsx)(Y,{open:Boolean(e),onOpenChange:e=>!e&&s(),children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(W,{container:n,children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(U,{className:"sp-dialog-overlay"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(J,{className:"sp-dialog","aria-describedby":"sp-rca-record-description",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-dialog__head sp-dialog__header",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(K,{className:"sp-dialog__title",children:r}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(B,{className:"sp-dialog__description",id:"sp-rca-record-description",children:e?.id?`${pe(e.kind)} ${pe(e.id)} · direct linked record`:`No linked ${String(e?.kind||"evidence").toLowerCase()} record was found.`})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(Q,{asChild:!0,children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(u,{label:"Close record preview",variant:"ghost",size:"icon",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(G,{size:18,"aria-hidden":"true"})})})]}),a.length?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-dialog__records",children:[a.slice(0,6).map((s,i)=>{const r=Object.entries(s).filter(([,e])=>null!==e&&""!==e);/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)("section",{className:"sp-dialog__record",children:[a.length>1&&/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("h3",{children:["Record ",i+1]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dl",{className:"sp-record-grid",children:r.slice(0,12).map(([e,s])=>/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-record sp-record-grid__item",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dt",{children:w(e)}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dd",{children:_e(s)})]},e))})]},`${String(e?.kind)}-${i}`)}),a.length>6&&/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("p",{className:"sp-dialog__more",children:["Showing 6 of ",l(a.length)," linked records."]})]}):/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(d,{title:"Evidence gap",detail:`No ${String(e?.kind||"evidence").toLowerCase()} is linked to this failure in Neo4j.`})]})]})})}function fe({row:e}){/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)("div",{className:"sp-rca-badges",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(b,{tone:ue(e.severity),children:w(e.severity)}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(b,{tone:xe(e.status),children:w(e.status)}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(b,{tone:e.has_rca?"green":"neutral",children:e.has_rca?"RCA linked":"RCA missing"})]})}function ge({rows:e,openFailure:s}){/* @__PURE__ */ /* @__PURE__ */
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
/* @__PURE__ */(0,oe.jsxs)("td",{className:"sp-table__primary",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("strong",{children:pe(e.equipment_name,"Unknown equipment")}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("small",{children:[pe(e.equipment_id)," · ",w(e.equipment_type)]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("td",{children:k(e.failure_date)}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("td",{className:"sp-table__primary",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("strong",{children:w(e.failure_mode)}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("small",{children:e.recurrence_count>1?`${l(e.recurrence_count)} matching causes`:"No matching recurrence"})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("td",{children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(b,{tone:ue(e.severity),children:w(e.severity)})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("td",{children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(b,{tone:xe(e.status),children:w(e.status)})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("td",{children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("span",{className:e.has_rca?"sp-rca__yes":"sp-rca__no",children:[e.has_rca?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(t,{size:16,"aria-hidden":"true"}):"—",/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{className:"sp-sr-only",children:e.has_rca?"RCA linked":"No RCA"})]})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("td",{children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(_,{variant:"ghost",size:"icon","aria-label":`Open failure ${e.failure_id}`,onClick:e=>{e.stopPropagation(),a()},children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(M,{className:"sp-rca__row-arrow",size:17,"aria-hidden":"true"})})})]},e.failure_id)})})]})})}function ye({rows:e,openFailure:s}){/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsx)("div",{className:"sp-mobile-list sp-rca__mobile-list",children:e.map(e=>/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("button",{className:"sp-mobile-card sp-rca-mobile-card",onClick:()=>s(e.failure_id),children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("span",{className:"sp-rca-mobile-card__topline",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{children:e.failure_id}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{children:k(e.failure_date)})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("strong",{children:pe(e.equipment_name,"Unknown equipment")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("small",{children:[pe(e.equipment_id)," · ",w(e.equipment_type)]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("span",{className:"sp-rca-mobile-card__mode",children:w(e.failure_mode)}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("span",{className:"sp-rca-mobile-card__footer",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(fe,{row:e}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(M,{size:17,"aria-hidden":"true"})]})]},e.failure_id))})}function be({steps:e,onPreview:s}){return e.length?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("div",{className:"sp-rca-chain","aria-label":"Linked evidence chain",children:e.map((a,i)=>{const r=(t=a.kind,{failure:re,rca:O,technician:ce,procedure:le,deviation:n,standard:I,document:se}[String(t||"").toLowerCase()]||X);var t;const c=!a.id;/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)(de.Fragment,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("button",{className:"sp-rca-chain__step"+(c?" sp-rca-chain__step--missing":""),onClick:()=>s(a),"aria-label":c?`Inspect missing ${pe(a.kind,"evidence")} link`:`Preview ${pe(a.kind)} ${pe(a.id)}`,children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("span",{className:"sp-rca-chain__icon",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(r,{size:17,"aria-hidden":"true"})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("span",{className:"sp-rca-chain__kind",children:pe(a.kind,"Evidence")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("strong",{children:pe(a.id,"Evidence gap")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("small",{children:pe(a.label,"Not linked")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(b,{tone:"RAG"===a.citation?"violet":"cyan",children:pe(a.citation,"Graph")})]}),i<e.length-1&&/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(M,{className:"sp-rca-chain__connector",size:16,"aria-hidden":"true"})]},`${String(a.kind)}-${i}`)})}):/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(d,{title:"No evidence chain found",detail:"This failure has no graph-linked evidence records."})}function Ne({detail:e}){const s=e.rca||{},a=e.technician||{},i=Array.isArray(e.documents)&&e.documents.length>0;/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)(g,{className:"sp-rca-panel",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(v,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(y,{children:"RCA narrative"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(c,{children:"Recorded finding, response, and procedure gap"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(b,{tone:s.rca_id?"indigo":"neutral",children:pe(s.rca_id,"No RCA")})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(x,{className:"sp-rca-narrative",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("article",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{className:"sp-rca-narrative__icon",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(P,{size:17,"aria-hidden":"true"})}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("h3",{children:"Root-cause finding"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("p",{children:pe(s.root_cause_text,"No root-cause finding is recorded.")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(b,{tone:"cyan",children:"Graph"})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("article",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{className:"sp-rca-narrative__icon",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(F,{size:17,"aria-hidden":"true"})}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("h3",{children:"Corrective action"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("p",{children:pe(s.corrective_action,"No corrective action is recorded.")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-rca-citations",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(b,{tone:"cyan",children:"Graph"}),i&&/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(b,{tone:"violet",children:"RAG"})]})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("article",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{className:"sp-rca-narrative__icon",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(le,{size:17,"aria-hidden":"true"})}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("h3",{children:"Procedure finding"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("p",{children:pe(s.violated_step,"No violated step is recorded.")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(b,{tone:"cyan",children:"Graph"})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-rca-byline",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("span",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(ce,{size:15,"aria-hidden":"true"})," Technician: ",
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("strong",{children:pe(a.name,"Unlinked")}),a.technician_id?` (${a.technician_id})`:""]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("span",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(ee,{size:15,"aria-hidden":"true"})," RCA date: ",
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("strong",{children:k(s.rca_date)})]})]})]})]})}function ke({tests:e}){/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)(g,{className:"sp-rca-panel",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(v,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(y,{children:"Downstream impact"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(c,{children:[l(e.length)," linked quality result",1===e.length?"":"s"]})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(te,{size:19,"aria-hidden":"true"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(x,{children:e.length?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(oe.Fragment,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("div",{className:"sp-rca-impact-wrap",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("table",{className:"sp-rca-impact",children:[
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
/* @__PURE__ */(0,oe.jsx)("td",{children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(b,{tone:String(e.result||"").toLowerCase().startsWith("fail")?"red":"green",children:pe(e.result)})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("td",{children:pe(e.standard_id)}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("td",{children:k(e.test_date)})]},pe(e.test_id,String(s))))})]})}),e.length>50&&/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("p",{className:"sp-rca-panel__note",children:["Showing 50 of ",l(e.length)," linked results."]})]}):/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(d,{title:"No downstream quality impact linked",detail:"No QualityTest is reachable through this failure’s deviations and coils."})})]})}function we({actions:e,checked:s,setChecked:a}){/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)(g,{className:"sp-rca-panel sp-rca-actions",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(v,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(y,{children:"Recommended action checklist"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(c,{children:"Deterministic actions derived from recorded RCA fields"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(T,{size:19,"aria-hidden":"true"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(x,{children:e.length?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("div",{className:"sp-rca-checklist",children:e.map((e,i)=>/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("label",{className:"sp-rca-checklist__item",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("input",{type:"checkbox",checked:Boolean(s[i]),onChange:e=>a(s=>({...s,[i]:e.target.checked})),"aria-label":`Mark action ${i+1} complete`}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("span",{className:"sp-rca-checklist__check",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(t,{size:14,"aria-hidden":"true"})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("span",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(b,{tone:"indigo",children:pe(e.role,"Owner")}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("p",{children:pe(e.text)})]})]},`${String(e.role)}-${i}`))}):/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(d,{title:"No role-scoped action available",detail:"No action can be derived from the recorded RCA fields."})})]})}function Ce({detail:e,openFailure:s}){const a=e.recurrences||[];/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)(g,{className:"sp-rca-panel sp-rca-sidebar-card",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(v,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(y,{children:"Recurrence"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(c,{children:"Exact normalized cause or action"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(ae,{size:18,"aria-hidden":"true"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(x,{children:e.recurrence_count?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(oe.Fragment,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-rca-recurrence__callout",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("strong",{children:l(e.recurrence_count)}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("span",{children:["other failure",1===e.recurrence_count?"":"s"," share this cause or corrective action"]})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-rca-recurrence__links",children:[a.slice(0,12).map(e=>/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("button",{onClick:()=>s(String(e.failure_id)),children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("span",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("strong",{children:pe(e.failure_id)}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("small",{children:w(e.failure_mode)})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(M,{size:15,"aria-hidden":"true"})]},pe(e.failure_id))),e.recurrence_count>12&&/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("small",{children:["+",l(e.recurrence_count-12)," more linked failures"]})]})]}):/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(d,{title:"No matching recurrence",detail:"No other RCA has the same normalized root-cause text or corrective action."})})]})}function Se({detail:e}){const s=e.confidence||{};/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)(g,{className:"sp-rca-panel sp-rca-sidebar-card",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(v,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(y,{children:"Confidence"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(c,{children:"Evidence-calibrated, no model self-scoring"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(z,{size:18,"aria-hidden":"true"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(x,{className:"sp-rca-confidence",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(b,{tone:je(s.level),children:w(s.level||"low")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("p",{children:pe(s.reason,"No confidence evidence is recorded.")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("dl",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dt",{children:"Sample size"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dd",{children:l(s.sample_size||1)})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dt",{children:"Source types"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dd",{children:l(s.corroborating_sources||0)})]})]})]})]})}function ze({detail:e}){const s=e.provenance||{};/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)(g,{className:"sp-rca-panel sp-rca-sidebar-card",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(v,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(y,{children:"Provenance"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(c,{children:"How this view was assembled"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(H,{size:18,"aria-hidden":"true"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(x,{className:"sp-rca-provenance",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(m,{children:"Direct Neo4j · no LLM"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("dl",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dt",{children:"Query mode"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dd",{children:w(s.query_mode||"direct_read_only_cypher")})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dt",{children:"LLM used"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("dd",{children:s.llm_used?"Yes":"No"})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("p",{children:pe(s.procedure_path,"Procedure link unavailable")})]})]})}function Ae({detail:e,failureId:s,loading:a,error:i,retry:r,goBack:n,openFailure:t}){const[d,o]=de.useState(null),[h,p]=de.useState({}),u=de.useRef(null);if(de.useEffect(()=>{const e=()=>{"rca"!==window.location.hash.replace(/^#\//,"").split("/")[0]&&o(null)};return window.addEventListener("hashchange",e),window.addEventListener("popstate",e),()=>{window.removeEventListener("hashchange",e),window.removeEventListener("popstate",e)}},[]),de.useEffect(()=>{o(null),p({})},[s]),de.useEffect(()=>{e&&u.current?.focus()},[e]),a&&!e)/* @__PURE__ */ /* @__PURE__ */return(0,oe.jsxs)("div",{className:"sp-rca-detail",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(_,{variant:"ghost",onClick:n,children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(E,{size:16,"aria-hidden":"true"})," All failures"]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(N,{label:`Loading ${s} evidence…`})]});if(i||!e)/* @__PURE__ */ /* @__PURE__ */return(0,oe.jsxs)("div",{className:"sp-rca-detail",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(_,{variant:"ghost",onClick:n,children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(E,{size:16,"aria-hidden":"true"})," All failures"]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(j,{error:i||`Failure ${s} was not found.`,retry:r})]});const m=e.failure||{},f=e.equipment||{},b={severity:e.severity,status:e.status,has_rca:Boolean(e.rca?.rca_id)};/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsxs)("div",{className:"sp-rca-detail",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("header",{className:"sp-detail-header sp-rca-detail__header",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)(_,{variant:"ghost",onClick:n,children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(E,{size:16,"aria-hidden":"true"})," All failures"]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-detail-header__title sp-rca-detail__identity",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("span",{className:"sp-eyebrow",children:["Failure evidence · ",pe(m.failure_id,s)]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("h1",{ref:u,tabIndex:-1,children:pe(f.name||f.equipment_id,"Unknown equipment")}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("p",{children:[pe(f.equipment_id)," · ",k(m.timestamp)," · ",w(m.failure_mode)]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("div",{className:"sp-detail-header__badges",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(fe,{row:b})})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)(g,{className:"sp-rca-panel sp-rca-evidence-card",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(v,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(y,{children:"Evidence chain"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(c,{children:"Focused graph trail · select any step to preview its record"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(X,{size:19,"aria-hidden":"true"})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(x,{children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(be,{steps:e.evidence_chain||[],onPreview:o})})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-detail-grid sp-rca-detail__grid",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(A,{className:"sp-tabs sp-stack sp-rca-detail__main",defaultValue:"analysis",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)(C,{className:"sp-tabs__list","aria-label":"Failure detail sections",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)(R,{className:"sp-tabs__trigger",value:"analysis",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(O,{size:15,"aria-hidden":"true"})," Analysis"]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)(R,{className:"sp-tabs__trigger",value:"impact",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(te,{size:15,"aria-hidden":"true"})," Downstream impact ",
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("span",{children:l(e.downstream_tests?.length||0)})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)(R,{className:"sp-tabs__trigger",value:"actions",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(T,{size:15,"aria-hidden":"true"})," Actions ",
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("span",{children:l(e.recommended_actions?.length||0)})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(S,{className:"sp-tabs__content",value:"analysis",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(Ne,{detail:e})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(S,{className:"sp-tabs__content",value:"impact",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(ke,{tests:e.downstream_tests||[]})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(S,{className:"sp-tabs__content",value:"actions",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(we,{actions:e.recommended_actions||[],checked:h,setChecked:p})})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("aside",{className:"sp-stack sp-rca-detail__sidebar",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(Ce,{detail:e,openFailure:t}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(Se,{detail:e}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(ze,{detail:e})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(ve,{step:d,onClose:()=>o(null)})]})}function Me({initialFailureId:e}){const[s,a]=de.useState(null),[r,n]=de.useState(!0),[t,_]=de.useState(""),[k,C]=de.useState(0),[S,z]=de.useState(he),[A,M]=de.useState(null),[R,E]=de.useState(!0),[F,T]=de.useState(""),[I,O]=de.useState(0),[P,U]=de.useState(e||null),[H,B]=de.useState(null),[G,Q]=de.useState(Boolean(e)),[W,J]=de.useState(""),[K,Y]=de.useState(0),X=de.useCallback(e=>{const s=String(e||"").trim();s&&(U(s),B(null),J(""),me(s))},[]),se=de.useCallback(()=>{U(null),B(null),J(""),me()},[]);de.useEffect(()=>{let e=!0;return n(!0),_(""),p("/api/rca/summary").then(s=>e&&a(s)).catch(s=>e&&_(s instanceof Error?s.message:String(s))).finally(()=>e&&n(!1)),()=>{e=!1}},[k]),de.useEffect(()=>{let e=!0;const s=new URLSearchParams;return S.equipmentType&&s.set("equipment_type",S.equipmentType),S.dateFrom&&s.set("date_from",S.dateFrom),S.dateTo&&s.set("date_to",S.dateTo),S.severity&&s.set("severity",S.severity),S.hasRca&&s.set("has_rca",S.hasRca),s.set("sort",S.sort||"recent"),E(!0),T(""),p(`/api/rca/failures?${s.toString()}`).then(s=>e&&M(s)).catch(s=>e&&T(s instanceof Error?s.message:String(s))).finally(()=>e&&E(!1)),()=>{e=!1}},[S,I]),de.useEffect(()=>{if(!P)return;let e=!0;return Q(!0),J(""),p(`/api/rca/failures/${encodeURIComponent(P)}`).then(s=>e&&B(s)).catch(s=>e&&J(s instanceof Error?s.message:String(s))).finally(()=>e&&Q(!1)),()=>{e=!1}},[P,K]),de.useEffect(()=>{e&&X(e)},[e,X]),de.useEffect(()=>{const e=e=>{const s=e.detail;let a="";if("string"==typeof s)a=s;else if(s&&"object"==typeof s){const e=s;a=String(e.failureId||e.failure_id||"")}a&&X(a)};return window.addEventListener("synapse-open-failure",e),()=>window.removeEventListener("synapse-open-failure",e)},[X]),de.useEffect(()=>{const e=()=>{const e=function(){const e=window.location.hash.replace(/^#\//,"").split("/");if("rca"!==e[0]||!e[1])return"";try{return decodeURIComponent(e.slice(1).join("/"))}catch{return e.slice(1).join("/")}}();U(e||null),e||(B(null),J(""))};return window.addEventListener("popstate",e),window.addEventListener("hashchange",e),()=>{window.removeEventListener("popstate",e),window.removeEventListener("hashchange",e)}},[]);const ae=A?.failures||[],re=(e,s)=>{z(a=>({...a,[e]:s}))};/* @__PURE__ */ /* @__PURE__ */
return(0,oe.jsx)("section",{className:"sp-rca","aria-label":"RCA and failures",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(q,{mode:"wait",initial:!1,children:P?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(i.div,{className:"sp-rca__view",initial:{opacity:0,x:18},animate:{opacity:1,x:0},exit:{opacity:0,x:12},transition:{duration:.2,ease:"easeOut"},children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(Ae,{detail:H,failureId:P,loading:G,error:W,retry:()=>Y(e=>e+1),goBack:se,openFailure:X})},`detail-${P}`):/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(i.div,{className:"sp-rca__view",initial:{opacity:0,x:-12},animate:{opacity:1,x:0},exit:{opacity:0,x:-12},transition:{duration:.2,ease:"easeOut"},children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(h,{eyebrow:"RCA & Failures",title:"Failure intelligence, fully traceable",description:"Move from an equipment event to its evidence, root cause, downstream impact, and response without losing the thread.",children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(m,{children:"Direct Neo4j · no LLM"})}),r&&!s?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(N,{label:"Loading failure overview…"}):t&&!s?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(j,{error:t,retry:()=>C(e=>e+1)}):s?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("section",{className:"sp-metrics sp-rca__metrics","aria-label":"RCA summary",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(o,{icon:L,index:0,label:"Total failures",value:l(s.total_failures),detail:"Tracked equipment events"}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(o,{icon:$,index:1,label:"RCA completion",value:`${Number(s.rca_completion_pct||0).toFixed(1)}%`,detail:`${l(s.failures_with_rca)} completed records`,featured:!0}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(o,{icon:D,index:2,label:"Most common mode",value:l(s.most_common_failure_mode?.count),detail:w(s.most_common_failure_mode?.name)}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(o,{icon:V,index:3,label:"Most affected equipment",value:l(s.most_affected_equipment?.count),detail:s.most_affected_equipment?.name||s.most_affected_equipment?.equipment_id||"—"})]}):null,
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)(g,{className:"sp-rca__browser",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(v,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(y,{children:"Failure register"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(c,{children:"Filter the operating history, then select a failure to follow its evidence."})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-rca__browser-actions",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(b,{tone:"indigo",children:R?"Updating…":`${l(A?.count||0)} failures`}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(u,{label:"Clear all filters",variant:"ghost",size:"icon",onClick:()=>z(he),disabled:Object.entries(S).every(([e,s])=>s===("sort"===e?"recent":"")),children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(Z,{size:16,"aria-hidden":"true"})}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(u,{label:"Refresh failure records",variant:"ghost",size:"icon",onClick:()=>O(e=>e+1),children:/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(ne,{size:16,"aria-hidden":"true"})})]})]}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(x,{children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-rca__filter-heading",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(ie,{size:16,"aria-hidden":"true"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{children:"Six ways to focus the register"})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("div",{className:"sp-fields sp-rca__filters",children:[
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(f,{label:"Equipment type",value:S.equipmentType,onValueChange:e=>re("equipmentType",e),placeholder:"All equipment",options:(s?.filters.equipment_types||[]).map(e=>({value:e,label:w(e)}))}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("label",{className:"sp-field",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{children:"From date"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("span",{className:"sp-date-input",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(ee,{size:15,"aria-hidden":"true"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("input",{type:"date",value:S.dateFrom,min:s?.filters.date_min||void 0,max:s?.filters.date_max||void 0,onChange:e=>re("dateFrom",e.target.value)})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsxs)("label",{className:"sp-field",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("span",{children:"To date"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)("span",{className:"sp-date-input",children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(ee,{size:15,"aria-hidden":"true"}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)("input",{type:"date",value:S.dateTo,min:s?.filters.date_min||void 0,max:s?.filters.date_max||void 0,onChange:e=>re("dateTo",e.target.value)})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(f,{label:"Severity",value:S.severity,onValueChange:e=>re("severity",e),placeholder:"All severities",options:(s?.filters.severities||[]).map(e=>({value:e,label:w(e)}))}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(f,{label:"RCA coverage",value:S.hasRca,onValueChange:e=>re("hasRca",e),placeholder:"All RCA states",options:[{value:"true",label:"RCA completed"},{value:"false",label:"RCA missing"}]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)(f,{label:"Sort by",value:S.sort,onValueChange:e=>re("sort",e||"recent"),options:[{value:"recent",label:"Most recent"},{value:"severe",label:"Highest severity"},{value:"recurring",label:"Most recurring"}]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,oe.jsx)("div",{className:"sp-rca__results","aria-live":"polite","aria-busy":R,children:R?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(N,{label:"Loading failure records…"}):F?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(j,{error:F,retry:()=>O(e=>e+1)}):ae.length?/* @__PURE__ */ /* @__PURE__ */(0,oe.jsxs)(oe.Fragment,{children:[/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(ge,{rows:ae,openFailure:X}),/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(ye,{rows:ae,openFailure:X})]}):/* @__PURE__ */ /* @__PURE__ */(0,oe.jsx)(d,{title:"No matching failures",detail:"Try widening the date range or clearing one of the filters."})})]})]})]},"failure-list")})})}export{Me as default};