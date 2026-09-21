const ROOT="https://www.tandjungsarihotel.com/";
const BLOCKED_JSON="/__sitecloner/blocked.json";
const BLANK_JS="/__sitecloner/blank.js";
const PLACEHOLDER="/__sitecloner/placeholder.svg";
(()=>{
  const asURL=(u)=>{try{return new URL(String(u&&u.url?u.url:u),location.href)}catch(e){return null}};
  const mapped=(u)=>{const a=asURL(u);if(!a)return null;if(M[a.href])return M[a.href];return null};
  const external=(u)=>{const a=asURL(u);return !!a&&a.origin!==location.origin&&!['data:','blob:','about:'].includes(a.protocol)};
  const localize=(u,fallback=BLOCKED_JSON)=>mapped(u)||(external(u)?fallback:u);
  const F=window.fetch;window.fetch=(u,o)=>{const hit=mapped(u);if(hit)return F.call(window,hit,o);if(external(u))return Promise.reject(new TypeError('External network disabled'));return F.call(window,u,o)};
  const O=XMLHttpRequest.prototype.open;XMLHttpRequest.prototype.open=function(m,u,...r){return O.call(this,m,localize(u,BLOCKED_JSON),...r)};
  if(navigator.sendBeacon){const B=navigator.sendBeacon.bind(navigator);navigator.sendBeacon=(u,d)=>external(u)?true:B(localize(u,BLOCKED_JSON),d)}
  for(const [C,n] of [[window.Worker,'Worker'],[window.SharedWorker,'SharedWorker']]){try{if(C)window[n]=function(u,o){return new C(localize(u,BLANK_JS),o)}}catch(e){}}
  try{const E=window.EventSource;if(E)window.EventSource=function(u,c){return new E(localize(u,BLOCKED_JSON),c)}}catch(e){}
  const fallback=(el)=>el instanceof HTMLScriptElement?BLANK_JS:el instanceof HTMLIFrameElement?'about:blank':el instanceof HTMLImageElement?PLACEHOLDER:BLOCKED_JSON;
  for(const [C,p] of [[HTMLImageElement,'src'],[HTMLScriptElement,'src'],[HTMLLinkElement,'href'],[HTMLVideoElement,'src'],[HTMLAudioElement,'src'],[HTMLSourceElement,'src'],[HTMLIFrameElement,'src']]){try{const d=Object.getOwnPropertyDescriptor(C.prototype,p);if(d&&d.set)Object.defineProperty(C.prototype,p,{...d,set(v){return d.set.call(this,localize(v,fallback(this)))}})}catch(e){}}
  try{const d=Object.getOwnPropertyDescriptor(HTMLAnchorElement.prototype,'href');if(d&&d.set)Object.defineProperty(HTMLAnchorElement.prototype,'href',{...d,set(v){return d.set.call(this,external(v)&&!mapped(v)?'#':localize(v,'#'))}})}catch(e){}
  const SA=Element.prototype.setAttribute;Element.prototype.setAttribute=function(n,v){const k=String(n).toLowerCase();if(k==='src'||k==='data'||(k==='href'&&this.tagName!=='A'))v=localize(v,fallback(this));if(k==='href'&&this.tagName==='A'&&external(v)&&!mapped(v))v='#';return SA.call(this,n,v)};
  document.addEventListener('click',e=>{const a=e.target&&e.target.closest?e.target.closest('a[href]'):null;if(a&&external(a.href)&&!mapped(a.href)){e.preventDefault();e.stopImmediatePropagation()}},true);
})();
