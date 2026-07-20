import{c as e,r as s,t as n}from"./jsx-runtime-BqTQeK5L.js";import{n as i}from"./dist-B9QpLl4r.js";import{G as r,_ as t,f as a,i as c,n as l,o as d,r as o,s as h,t as p}from"./ui-B61WkjWT.js";import{t as x}from"./book-open-check-D8hdXL6T.js";import{a as j,i as u,n as m,r as g,t as v}from"./sparkles-C1ZyXJN8.js";import{t as f}from"./rotate-ccw-BZLzTzUS.js";var k=r("circle-user-round",[["path",{d:"M17.925 20.056a6 6 0 0 0-11.851.001",key:"z69sun"}],["circle",{cx:"12",cy:"11",r:"4",key:"1gt34v"}],["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}]]),w=r("headphones",[["path",{d:"M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3",key:"1xhozi"}]]),y=r("mic-off",[["path",{d:"M12 19v3",key:"npa21l"}],["path",{d:"M15 9.34V5a3 3 0 0 0-5.68-1.33",key:"1gzdoj"}],["path",{d:"M16.95 16.95A7 7 0 0 1 5 12v-2",key:"cqa7eg"}],["path",{d:"M18.89 13.23A7 7 0 0 0 19 12v-2",key:"16hl24"}],["path",{d:"m2 2 20 20",key:"1ooewy"}],["path",{d:"M9 9v3a3 3 0 0 0 5.12 2.12",key:"r2i35w"}]]),S=r("mic",[["path",{d:"M12 19v3",key:"npa21l"}],["path",{d:"M19 10v2a7 7 0 0 1-14 0v-2",key:"1vc78b"}],["rect",{x:"9",y:"2",width:"6",height:"13",rx:"3",key:"s6n7sd"}]]),N=r("search",[["path",{d:"m21 21-4.34-4.34",key:"14j7rj"}],["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}]]),_=r("send",[["path",{d:"M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z",key:"1ffxy3"}],["path",{d:"m21.854 2.147-10.94 10.939",key:"12cjpa"}]]),b=r("volume-2",[["path",{d:"M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z",key:"uqj9uw"}],["path",{d:"M16 9a5 5 0 0 1 0 6",key:"1q6k2b"}],["path",{d:"M19.364 18.364a9 9 0 0 0 0-12.728",key:"ijwkga"}]]),z=/* @__PURE__ */e(s(),1),C=n(),R={name:"Arvind Rao",role:"Senior Furnace Equipment Engineer",equipment:["Reheating Furnace #1","Reheating Furnace #2","Cooling-water circuit"],years_of_experience:34,known_rcas:["RCA1186 — insufficient heat dissipation","RCA1120 — burner instability"]},E=["Background and expertise","Case-specific furnace incidents","Tacit diagnostic reasoning","Exceptions and safety boundaries"],A="synapse_knowledge_transfer_demo",M=["Unverified","Peer Confirmed","Approved"];function I(e){if(!("speechSynthesis"in window))return;window.speechSynthesis.cancel();const s=new SpeechSynthesisUtterance(e.replace("[INTERVIEW_COMPLETE]","").trim());s.lang="en-IN",s.rate=.96,window.speechSynthesis.speak(s)}function q(e){return[e.title,e.asset,e.situation,...e.symptoms,e.diagnostic_reasoning,...e.recommended_checks,e.exceptions,e.safety_warning].join(" ")}function T(e){return e.toLowerCase().match(/[a-z0-9]+/g)?.filter(e=>e.length>2)||[]}function $({value:e}){/* @__PURE__ */ /* @__PURE__ */
return(0,C.jsx)(p,{tone:"Approved"===e?"green":"Peer Confirmed"===e?"cyan":"amber",children:e})}function K({card:e,index:s,onVerify:n}){/* @__PURE__ */ /* @__PURE__ */
return(0,C.jsxs)(o,{className:"sp-kt-card",children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(d,{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("span",{className:"sp-kt-card__number",children:["Knowledge card ",String(s+1).padStart(2,"0")]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(h,{children:e.title||"Untitled operational knowledge"})]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("button",{className:"sp-kt-verification",onClick:n,title:"Click to advance verification",children:/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)($,{value:e.verification})})]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(c,{children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("div",{className:"sp-kt-facts",children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("span",{children:"Asset"}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("strong",{children:e.asset||"Not specified"})]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("span",{children:"Situation"}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("strong",{children:e.situation||"Not specified"})]})]}),e.symptoms.length>0&&/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("section",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("h4",{children:"Symptoms"}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("ul",{children:e.symptoms.map((e,s)=>/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("li",{children:e},s))})]}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("section",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("h4",{children:"Diagnostic reasoning"}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("p",{children:e.diagnostic_reasoning||"No explicit diagnostic criteria captured."})]}),e.recommended_checks.length>0&&/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("section",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("h4",{children:"Recommended checks"}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("ol",{children:e.recommended_checks.map((e,s)=>/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("li",{children:e},s))})]}),(e.exceptions||e.safety_warning)&&/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{className:"sp-kt-guardrails",children:[e.exceptions&&/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("span",{children:"Exception"}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("p",{children:e.exceptions})]}),e.safety_warning&&/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{className:"is-safety",children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("span",{children:"Safety warning"}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("p",{children:e.safety_warning})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("footer",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("span",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)(k,{size:13})," ",e.contributor||R.name]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("span",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)(g,{size:13})," ",e.source||"Interview transcript"]})]})]})]})}function P(){const[e,s]=z.useState("ready"),[n,r]=z.useState(""),[g,P]=z.useState(""),[F,O]=z.useState([]),[U,V]=z.useState([]),[H,L]=z.useState(!1),[D,B]=z.useState(""),[W,Y]=z.useState(!1),[J,Q]=z.useState(""),[G,X]=z.useState(void 0),Z=z.useRef(null),ee=z.useRef(""),se=Boolean(window.SpeechRecognition||window.webkitSpeechRecognition);async function ne(e){const n=await t("/api/knowledge-transfer/interview",{profile:R,plan:E,transcript:e}),i=n.message.replace("[INTERVIEW_COMPLETE]","").trim();i&&I(i),n.complete?await ie(e):(r(i),s("interview"))}async function ie(e){s("extracting"),r(""),L(!0);try{const n=await t("/api/knowledge-transfer/extract",{profile:R,transcript:e});V(n.cards.map(e=>({...e,verification:"Unverified"}))),s("complete"),i.success(`${n.cards.length} knowledge card${1===n.cards.length?"":"s"} extracted for review`)}catch(n){B(n instanceof Error?n.message:String(n)),s("interview")}finally{L(!1)}}async function re(){const e=g.trim();if(!e||!n||H)return;Z.current?.stop(),Y(!1);const s=[...F,{question:n,answer:e}];O(s),P(""),L(!0),B("");try{s.length>=10?await ie(s):await ne(s)}catch(i){B(i instanceof Error?i.message:String(i))}finally{L(!1)}}z.useEffect(()=>{try{const e=JSON.parse(localStorage.getItem(A)||"null");e?.cards?.length&&(V(e.cards),O(e.transcript||[]),s("complete"))}catch{}},[]),z.useEffect(()=>{if(U.length)try{localStorage.setItem(A,JSON.stringify({cards:U,transcript:F}))}catch{}},[U,F]),z.useEffect(()=>()=>{Z.current?.stop(),window.speechSynthesis?.cancel()},[]);const te=Math.min(100,Math.round(F.length/10*100));/* @__PURE__ */ /* @__PURE__ */
return(0,C.jsx)("main",{className:"sp-kt",children:/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{className:"sp-kt__inner",children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)(a,{eyebrow:"Institutional knowledge",title:"Knowledge Transfer Interview",description:"Capture hard-earned furnace expertise through an adaptive voice interview, then turn it into reviewable and governed knowledge cards.",children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(p,{tone:"violet",children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(v,{size:12})," Tencent HY3 · OpenRouter"]}),("ready"!==e||U.length>0)&&/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(l,{size:"sm",variant:"outline",onClick:function(){Z.current?.stop(),window.speechSynthesis?.cancel(),localStorage.removeItem(A),s("ready"),r(""),P(""),O([]),V([]),B(""),Q(""),X(void 0)},children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(f,{size:13})," Reset demo"]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("div",{className:"sp-kt-profile",children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)(o,{children:/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(c,{children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("div",{className:"sp-kt-profile__avatar",children:"AR"}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("div",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("span",{children:"Retiring employee"}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("h2",{children:R.name}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("p",{children:[R.role," · ",R.years_of_experience," years"]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)(p,{tone:"amber",children:"High knowledge risk"})]})}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)(o,{children:/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(c,{children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("span",{children:"Known operational context"}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("strong",{children:[R.equipment.length," critical systems"]}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("p",{children:R.equipment.join(" · ")})]})}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)(o,{children:/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(c,{children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("span",{children:"Interview plan"}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("strong",{children:[E.length," structured topics"]}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("p",{children:"Background · Cases · Reasoning · Safety"})]})})]}),"ready"===e&&/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(o,{className:"sp-kt-start",children:/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(c,{children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("div",{className:"sp-kt-start__icon",children:/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(w,{size:30})}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("h2",{children:"Ready to preserve Arvind's expertise?"}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("p",{children:"Synapse will use his verified profile and RCA history to ask one focused question at a time. Answers can be spoken or typed."}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("div",{className:"sp-kt-plan",children:E.map((e,s)=>/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("span",{children:s+1}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("strong",{children:e}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)(j,{size:15})]},e))}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)(l,{onClick:async function(){L(!0),B(""),V([]),O([]),X(void 0);try{await ne([])}catch(e){B(e instanceof Error?e.message:String(e)),s("ready")}finally{L(!1)}},disabled:H,children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)(S,{size:16})," ",H?"Preparing interview…":"Start voice interview"]})]})}),("interview"===e||"extracting"===e)&&/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{className:"sp-kt-interview",children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("section",{className:"sp-kt-conversation",children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("div",{className:"sp-kt-progress",children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("span",{children:"Interview progress"}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("strong",{children:[F.length," of 10 maximum exchanges"]})]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("div",{children:/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("i",{style:{width:`${te}%`}})})]}),F.map((e,s)=>/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{className:"sp-kt-exchange",children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{className:"is-ai",children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(v,{size:15}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("p",{children:e.question})]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{className:"is-person",children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(k,{size:15}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("p",{children:e.answer})]})]},s)),"extracting"===e?/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{className:"sp-kt-extracting",children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)(v,{size:24}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("strong",{children:"Structuring the interview into knowledge cards…"}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("p",{children:"The original Q/A transcript remains unchanged."})]}):/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(C.Fragment,{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{className:"sp-kt-current",children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{className:"sp-kt-current__label",children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("span",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(v,{size:14})," Synapse interviewer"]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("button",{onClick:()=>I(n),"aria-label":"Read question aloud",children:/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(b,{size:15})})]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("p",{children:H&&!n?"Preparing the next question…":n})]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{className:"sp-kt-answer",children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("label",{htmlFor:"kt-answer",children:"Your answer"}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("textarea",{id:"kt-answer",value:g,onChange:e=>P(e.target.value),placeholder:"Speak or type your experience here…",rows:5,disabled:H,onKeyDown:e=>{"Enter"===e.key&&(e.ctrlKey||e.metaKey)&&re()}}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("span",{children:se?"Mic and text are both available":"Speech recognition unavailable — text still works"}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(l,{variant:W?"danger":"outline",onClick:function(){if(!se)return;if(W)return Z.current?.stop(),void Y(!1);const e=window.SpeechRecognition||window.webkitSpeechRecognition;if(!e)return;const s=new e;ee.current=g.trim()?`${g.trim()} `:"",s.continuous=!0,s.interimResults=!0,s.lang="en-IN",s.onresult=e=>{let s="",n="";for(let i=0;i<e.results.length;i+=1){const r=e.results[i][0]?.transcript||"";e.results[i].isFinal?s+=`${r} `:n+=r}s&&(ee.current+=s),P(`${ee.current}${n}`.trim())},s.onend=()=>Y(!1),s.onerror=()=>{Y(!1),B("Voice recognition stopped. You can continue in the text box.")},Z.current=s;try{s.start(),Y(!0),B("")}catch{B("The microphone could not start. Type your answer instead.")}},disabled:!se||H,children:[W?/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(y,{size:15}):/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(S,{size:15}),W?"Stop listening":"Speak"]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(l,{onClick:re,disabled:!g.trim()||H,children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)(_,{size:15})," ",H?"Thinking…":"Submit answer"]})]})]})]})]})]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("aside",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(o,{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(d,{children:/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(h,{children:"Evidence context"})}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(c,{children:/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{className:"sp-kt-context",children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("span",{children:"Profile"}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("strong",{children:R.role}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("span",{children:"Equipment"}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("strong",{children:R.equipment.join(", ")}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("span",{children:"Known RCAs"}),R.known_rcas.map(e=>/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("strong",{children:e},e))]})})]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(o,{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(d,{children:/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(h,{children:"Capture safeguards"})}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(c,{children:/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("ul",{className:"sp-kt-safeguards",children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("li",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(u,{size:14})," Original Q/A is retained"]}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("li",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(m,{size:14})," Cards begin unverified"]}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("li",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(x,{size:14})," Human approval stays separate"]})]})})]})]})]}),D&&/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{className:"sp-kt-error",role:"alert",children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("strong",{children:"Knowledge Transfer could not continue."}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("span",{children:D})]}),"complete"===e&&/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(C.Fragment,{children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("div",{className:"sp-kt-results-head",children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("span",{children:"Extraction complete"}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("h2",{children:[U.length," knowledge cards ready for review"]}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("p",{children:"Click a verification badge to cycle from Unverified to Peer Confirmed to Approved."})]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(p,{tone:"amber",children:[U.filter(e=>"Unverified"===e.verification).length," unverified"]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(p,{tone:"green",children:[U.filter(e=>"Approved"===e.verification).length," approved"]})]})]}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("div",{className:"sp-kt-cards",children:U.map((e,s)=>/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(K,{card:e,index:s,onVerify:()=>function(e){V(s=>s.map((s,n)=>n===e?{...s,verification:M[(M.indexOf(s.verification)+1)%M.length]}:s))}(s)},`${e.title}-${s}`))}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)(o,{className:"sp-kt-rag",children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(d,{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(h,{children:"Ask the captured knowledge"}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("p",{children:"Demo governed retrieval using a transparent keyword match across these cards."})]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(p,{tone:"indigo",children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(N,{size:12})," Local card retrieval"]})]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(c,{children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("form",{onSubmit:function(e){e.preventDefault();const s=new Set(T(J)),n=U.map(e=>({card:e,score:T(q(e)).reduce((e,n)=>e+(s.has(n)?1:0),0)})).sort((e,s)=>s.score-e.score);X(n[0]?.score>0?n[0].card:null)},children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("input",{value:J,onChange:e=>Q(e.target.value),placeholder:"What should I check when furnace temperature rises unevenly?"}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)(l,{type:"submit",disabled:!J.trim(),children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)(N,{size:15})," Ask"]})]}),null===G&&/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("div",{className:"sp-kt-rag__empty",children:"No captured knowledge card shares meaningful keywords with that question."}),G&&/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("div",{className:"sp-kt-rag__answer",children:[
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("strong",{children:G.title}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsx)("p",{children:G.diagnostic_reasoning}),G.recommended_checks.length>0&&/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("ol",{children:G.recommended_checks.map((e,s)=>/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)("li",{children:e},s))}),
/* @__PURE__ */
/* @__PURE__ */(0,C.jsxs)("footer",{children:[/* @__PURE__ */ /* @__PURE__ */(0,C.jsxs)("span",{children:["Citation: ",G.contributor||R.name," · ",G.source||"Interview transcript"]}),/* @__PURE__ */ /* @__PURE__ */(0,C.jsx)($,{value:G.verification})]})]})]})]})]})]})})}export{P as default};