import{c as Re,e as j,r as C,d as f,o as K,f as p,t as Le,w as Ge,R as Xe,h as w,s as Te,g as Je,j as Ye,Q as G,k as xe,l as U,m as Ze,p as O,u as et,q as tt,v as M,x as Pe,y as $e,n as Se,z as ce,A as ze,B as nt,C as ot,D as lt,E as at,F as Ie,G as ee,H as it,I as rt,J as ut,K as st,L as ct,M as dt,N as te,O as H,P as re,S as ft}from"./index.6ccca0c4.js";import{u as vt,a as ue,b as Ce,r as ht,g as bt,c as gt,d as mt,e as se}from"./scroll.b7bad442.js";import{u as yt,Q as wt,a as Tt}from"./use-quasar.b4f6a83d.js";import{u as St,a as Ct,b as qt}from"./use-checkbox.19eb54f4.js";let kt=0;const _t=["click","keydown"],Rt={icon:String,label:[Number,String],alert:[Boolean,String],alertIcon:String,name:{type:[Number,String],default:()=>`t_${kt++}`},noCaps:Boolean,tabindex:[String,Number],disable:Boolean,contentClass:String,ripple:{type:[Boolean,Object],default:!0}};function Lt(e,T,a,o){const n=Re(Le,j);if(n===j)return console.error("QTab/QRouteTab component needs to be child of QTabs"),j;const{proxy:g}=U(),m=C(null),L=C(null),h=C(null),c=f(()=>e.disable===!0||e.ripple===!1?!1:Object.assign({keyCodes:[13,32],early:!0},e.ripple===!0?{}:e.ripple)),R=f(()=>n.currentModel.value===e.name),$=f(()=>"q-tab relative-position self-stretch flex flex-center text-center"+(R.value===!0?" q-tab--active"+(n.tabProps.value.activeClass?" "+n.tabProps.value.activeClass:"")+(n.tabProps.value.activeColor?` text-${n.tabProps.value.activeColor}`:"")+(n.tabProps.value.activeBgColor?` bg-${n.tabProps.value.activeBgColor}`:""):" q-tab--inactive")+(e.icon&&e.label&&n.tabProps.value.inlineLabel===!1?" q-tab--full":"")+(e.noCaps===!0||n.tabProps.value.noCaps===!0?" q-tab--no-caps":"")+(e.disable===!0?" disabled":" q-focusable q-hoverable cursor-pointer")+(o!==void 0?o.linkClass.value:"")),P=f(()=>"q-tab__content self-stretch flex-center relative-position q-anchor--skip non-selectable "+(n.tabProps.value.inlineLabel===!0?"row no-wrap q-tab__content--inline":"column")+(e.contentClass!==void 0?` ${e.contentClass}`:"")),d=f(()=>e.disable===!0||n.hasFocus.value===!0||R.value===!1&&n.hasActiveTab.value===!0?-1:e.tabindex||0);function q(i,r){if(r!==!0&&m.value!==null&&m.value.focus(),e.disable===!0){o!==void 0&&o.hasRouterLink.value===!0&&Te(i);return}if(o===void 0){n.updateModel({name:e.name}),a("click",i);return}if(o.hasRouterLink.value===!0){const b=(S={})=>{let x;const I=S.to===void 0||Ze(S.to,e.to)===!0?n.avoidRouteWatcher=vt():null;return o.navigateToRouterLink(i,{...S,returnRouterError:!0}).catch(Q=>{x=Q}).then(Q=>{if(I===n.avoidRouteWatcher&&(n.avoidRouteWatcher=!1,x===void 0&&(Q===void 0||Q.message.startsWith("Avoided redundant navigation")===!0)&&n.updateModel({name:e.name})),S.returnRouterError===!0)return x!==void 0?Promise.reject(x):Q})};a("click",i,b),i.defaultPrevented!==!0&&b();return}a("click",i)}function B(i){Je(i,[13,32])?q(i,!0):Ye(i)!==!0&&i.keyCode>=35&&i.keyCode<=40&&i.altKey!==!0&&i.metaKey!==!0&&n.onKbdNavigate(i.keyCode,g.$el)===!0&&Te(i),a("keydown",i)}function E(){const i=n.tabProps.value.narrowIndicator,r=[],b=w("div",{ref:h,class:["q-tab__indicator",n.tabProps.value.indicatorClass]});e.icon!==void 0&&r.push(w(G,{class:"q-tab__icon",name:e.icon})),e.label!==void 0&&r.push(w("div",{class:"q-tab__label"},e.label)),e.alert!==!1&&r.push(e.alertIcon!==void 0?w(G,{class:"q-tab__alert-icon",color:e.alert!==!0?e.alert:void 0,name:e.alertIcon}):w("div",{class:"q-tab__alert"+(e.alert!==!0?` text-${e.alert}`:"")})),i===!0&&r.push(b);const S=[w("div",{class:"q-focus-helper",tabindex:-1,ref:m}),w("div",{class:P.value},xe(T.default,r))];return i===!1&&S.push(b),S}const A={name:f(()=>e.name),rootRef:L,tabIndicatorRef:h,routeData:o};K(()=>{n.unregisterTab(A)}),p(()=>{n.registerTab(A)});function u(i,r){const b={ref:L,class:$.value,tabindex:d.value,role:"tab","aria-selected":R.value===!0?"true":"false","aria-disabled":e.disable===!0?"true":void 0,onClick:q,onKeydown:B,...r};return Ge(w(i,b,E()),[[Xe,c.value]])}return{renderTab:u,$tabs:n}}var qe=O({name:"QRouteTab",props:{...et,...Rt},emits:_t,setup(e,{slots:T,emit:a}){const o=tt({useDisableForRouterLinkProps:!1}),{renderTab:n,$tabs:g}=Lt(e,T,a,{exact:f(()=>e.exact),...o});return M(()=>`${e.name} | ${e.exact} | ${(o.resolvedLink.value||{}).href}`,()=>{g.verifyRouteModel()}),()=>n(o.linkTag.value,o.linkAttrs.value)}});function xt(){const e=C(!Pe.value);return e.value===!1&&p(()=>{e.value=!0}),e}const Me=typeof ResizeObserver!="undefined",ke=Me===!0?{}:{style:"display:block;position:absolute;top:0;left:0;right:0;bottom:0;height:100%;width:100%;overflow:hidden;pointer-events:none;z-index:-1;",url:"about:blank"};var ne=O({name:"QResizeObserver",props:{debounce:{type:[String,Number],default:100}},emits:["resize"],setup(e,{emit:T}){let a=null,o,n={width:-1,height:-1};function g(h){h===!0||e.debounce===0||e.debounce==="0"?m():a===null&&(a=setTimeout(m,e.debounce))}function m(){if(a!==null&&(clearTimeout(a),a=null),o){const{offsetWidth:h,offsetHeight:c}=o;(h!==n.width||c!==n.height)&&(n={width:h,height:c},T("resize",n))}}const{proxy:L}=U();if(Me===!0){let h;const c=R=>{o=L.$el.parentNode,o?(h=new ResizeObserver(g),h.observe(o),m()):R!==!0&&Se(()=>{c(!0)})};return p(()=>{c()}),K(()=>{a!==null&&clearTimeout(a),h!==void 0&&(h.disconnect!==void 0?h.disconnect():o&&h.unobserve(o))}),$e}else{let R=function(){a!==null&&(clearTimeout(a),a=null),c!==void 0&&(c.removeEventListener!==void 0&&c.removeEventListener("resize",g,ce.passive),c=void 0)},$=function(){R(),o&&o.contentDocument&&(c=o.contentDocument.defaultView,c.addEventListener("resize",g,ce.passive),m())};const h=xt();let c;return p(()=>{Se(()=>{o=L.$el,o&&$()})}),K(R),L.trigger=g,()=>{if(h.value===!0)return w("object",{style:ke.style,tabindex:-1,type:"text/html",data:ke.url,"aria-hidden":"true",onLoad:$})}}}});function Pt(e,T,a){const o=a===!0?["left","right"]:["top","bottom"];return`absolute-${T===!0?o[0]:o[1]}${e?` text-${e}`:""}`}const $t=["left","center","right","justify"];var zt=O({name:"QTabs",props:{modelValue:[Number,String],align:{type:String,default:"center",validator:e=>$t.includes(e)},breakpoint:{type:[String,Number],default:600},vertical:Boolean,shrink:Boolean,stretch:Boolean,activeClass:String,activeColor:String,activeBgColor:String,indicatorColor:String,leftIcon:String,rightIcon:String,outsideArrows:Boolean,mobileArrows:Boolean,switchIndicator:Boolean,narrowIndicator:Boolean,inlineLabel:Boolean,noCaps:Boolean,dense:Boolean,contentClass:String,"onUpdate:modelValue":[Function,Array]},setup(e,{slots:T,emit:a}){const{proxy:o}=U(),{$q:n}=o,{registerTick:g}=ue(),{registerTick:m}=ue(),{registerTick:L}=ue(),{registerTimeout:h,removeTimeout:c}=Ce(),{registerTimeout:R,removeTimeout:$}=Ce(),P=C(null),d=C(null),q=C(e.modelValue),B=C(!1),E=C(!0),A=C(!1),u=C(!1),i=[],r=C(0),b=C(!1);let S=null,x=null,I;const Q=f(()=>({activeClass:e.activeClass,activeColor:e.activeColor,activeBgColor:e.activeBgColor,indicatorClass:Pt(e.indicatorColor,e.switchIndicator,e.vertical),narrowIndicator:e.narrowIndicator,inlineLabel:e.inlineLabel,noCaps:e.noCaps})),Be=f(()=>{const t=r.value,l=q.value;for(let s=0;s<t;s++)if(i[s].name.value===l)return!0;return!1}),Ae=f(()=>`q-tabs__content--align-${B.value===!0?"left":u.value===!0?"justify":e.align}`),Qe=f(()=>`q-tabs row no-wrap items-center q-tabs--${B.value===!0?"":"not-"}scrollable q-tabs--${e.vertical===!0?"vertical":"horizontal"} q-tabs__arrows--${e.outsideArrows===!0?"outside":"inside"} q-tabs--mobile-with${e.mobileArrows===!0?"":"out"}-arrows`+(e.dense===!0?" q-tabs--dense":"")+(e.shrink===!0?" col-shrink":"")+(e.stretch===!0?" self-stretch":"")),Ee=f(()=>"q-tabs__content scroll--mobile row no-wrap items-center self-stretch hide-scrollbar relative-position "+Ae.value+(e.contentClass!==void 0?` ${e.contentClass}`:"")),X=f(()=>e.vertical===!0?{container:"height",content:"offsetHeight",scroll:"scrollHeight"}:{container:"width",content:"offsetWidth",scroll:"scrollWidth"}),J=f(()=>e.vertical!==!0&&n.lang.rtl===!0),oe=f(()=>ht===!1&&J.value===!0);M(J,N),M(()=>e.modelValue,t=>{le({name:t,setCurrent:!0,skipEmit:!0})}),M(()=>e.outsideArrows,Y);function le({name:t,setCurrent:l,skipEmit:s}){q.value!==t&&(s!==!0&&e["onUpdate:modelValue"]!==void 0&&a("update:modelValue",t),(l===!0||e["onUpdate:modelValue"]===void 0)&&(Ve(q.value,t),q.value=t))}function Y(){g(()=>{de({width:P.value.offsetWidth,height:P.value.offsetHeight})})}function de(t){if(X.value===void 0||d.value===null)return;const l=t[X.value.container],s=Math.min(d.value[X.value.scroll],Array.prototype.reduce.call(d.value.children,(_,y)=>_+(y[X.value.content]||0),0)),k=l>0&&s>l;B.value=k,k===!0&&m(N),u.value=l<parseInt(e.breakpoint,10)}function Ve(t,l){const s=t!=null&&t!==""?i.find(_=>_.name.value===t):null,k=l!=null&&l!==""?i.find(_=>_.name.value===l):null;if(s&&k){const _=s.tabIndicatorRef.value,y=k.tabIndicatorRef.value;S!==null&&(clearTimeout(S),S=null),_.style.transition="none",_.style.transform="none",y.style.transition="none",y.style.transform="none";const v=_.getBoundingClientRect(),z=y.getBoundingClientRect();y.style.transform=e.vertical===!0?`translate3d(0,${v.top-z.top}px,0) scale3d(1,${z.height?v.height/z.height:1},1)`:`translate3d(${v.left-z.left}px,0,0) scale3d(${z.width?v.width/z.width:1},1,1)`,L(()=>{S=setTimeout(()=>{S=null,y.style.transition="transform .25s cubic-bezier(.4, 0, .2, 1)",y.style.transform="none"},70)})}k&&B.value===!0&&W(k.rootRef.value)}function W(t){const{left:l,width:s,top:k,height:_}=d.value.getBoundingClientRect(),y=t.getBoundingClientRect();let v=e.vertical===!0?y.top-k:y.left-l;if(v<0){d.value[e.vertical===!0?"scrollTop":"scrollLeft"]+=Math.floor(v),N();return}v+=e.vertical===!0?y.height-_:y.width-s,v>0&&(d.value[e.vertical===!0?"scrollTop":"scrollLeft"]+=Math.ceil(v),N())}function N(){const t=d.value;if(t===null)return;const l=t.getBoundingClientRect(),s=e.vertical===!0?t.scrollTop:Math.abs(t.scrollLeft);J.value===!0?(E.value=Math.ceil(s+l.width)<t.scrollWidth-1,A.value=s>0):(E.value=s>0,A.value=e.vertical===!0?Math.ceil(s+l.height)<t.scrollHeight:Math.ceil(s+l.width)<t.scrollWidth)}function fe(t){x!==null&&clearInterval(x),x=setInterval(()=>{Fe(t)===!0&&D()},5)}function ve(){fe(oe.value===!0?Number.MAX_SAFE_INTEGER:0)}function he(){fe(oe.value===!0?0:Number.MAX_SAFE_INTEGER)}function D(){x!==null&&(clearInterval(x),x=null)}function He(t,l){const s=Array.prototype.filter.call(d.value.children,z=>z===l||z.matches&&z.matches(".q-tab.q-focusable")===!0),k=s.length;if(k===0)return;if(t===36)return W(s[0]),s[0].focus(),!0;if(t===35)return W(s[k-1]),s[k-1].focus(),!0;const _=t===(e.vertical===!0?38:37),y=t===(e.vertical===!0?40:39),v=_===!0?-1:y===!0?1:void 0;if(v!==void 0){const z=J.value===!0?-1:1,V=s.indexOf(l)+v*z;return V>=0&&V<k&&(W(s[V]),s[V].focus({preventScroll:!0})),!0}}const De=f(()=>oe.value===!0?{get:t=>Math.abs(t.scrollLeft),set:(t,l)=>{t.scrollLeft=-l}}:e.vertical===!0?{get:t=>t.scrollTop,set:(t,l)=>{t.scrollTop=l}}:{get:t=>t.scrollLeft,set:(t,l)=>{t.scrollLeft=l}});function Fe(t){const l=d.value,{get:s,set:k}=De.value;let _=!1,y=s(l);const v=t<y?-1:1;return y+=v*5,y<0?(_=!0,y=0):(v===-1&&y<=t||v===1&&y>=t)&&(_=!0,y=t),k(l,y),N(),_}function be(t,l){for(const s in t)if(t[s]!==l[s])return!1;return!0}function Oe(){let t=null,l={matchedLen:0,queryDiff:9999,hrefLen:0};const s=i.filter(v=>v.routeData!==void 0&&v.routeData.hasRouterLink.value===!0),{hash:k,query:_}=o.$route,y=Object.keys(_).length;for(const v of s){const z=v.routeData.exact.value===!0;if(v.routeData[z===!0?"linkIsExactActive":"linkIsActive"].value!==!0)continue;const{hash:V,query:ae,matched:Ue,href:pe}=v.routeData.resolvedLink.value,ie=Object.keys(ae).length;if(z===!0){if(V!==k||ie!==y||be(_,ae)===!1)continue;t=v.name.value;break}if(V!==""&&V!==k||ie!==0&&be(ae,_)===!1)continue;const F={matchedLen:Ue.length,queryDiff:y-ie,hrefLen:pe.length-V.length};if(F.matchedLen>l.matchedLen){t=v.name.value,l=F;continue}else if(F.matchedLen!==l.matchedLen)continue;if(F.queryDiff<l.queryDiff)t=v.name.value,l=F;else if(F.queryDiff!==l.queryDiff)continue;F.hrefLen>l.hrefLen&&(t=v.name.value,l=F)}t===null&&i.some(v=>v.routeData===void 0&&v.name.value===q.value)===!0||le({name:t,setCurrent:!0})}function We(t){if(c(),b.value!==!0&&P.value!==null&&t.target&&typeof t.target.closest=="function"){const l=t.target.closest(".q-tab");l&&P.value.contains(l)===!0&&(b.value=!0,B.value===!0&&W(l))}}function Ne(){h(()=>{b.value=!1},30)}function Z(){me.avoidRouteWatcher===!1?R(Oe):$()}function ge(){if(I===void 0){const t=M(()=>o.$route.fullPath,Z);I=()=>{t(),I=void 0}}}function je(t){i.push(t),r.value++,Y(),t.routeData===void 0||o.$route===void 0?R(()=>{if(B.value===!0){const l=q.value,s=l!=null&&l!==""?i.find(k=>k.name.value===l):null;s&&W(s.rootRef.value)}}):(ge(),t.routeData.hasRouterLink.value===!0&&Z())}function Ke(t){i.splice(i.indexOf(t),1),r.value--,Y(),I!==void 0&&t.routeData!==void 0&&(i.every(l=>l.routeData===void 0)===!0&&I(),Z())}const me={currentModel:q,tabProps:Q,hasFocus:b,hasActiveTab:Be,registerTab:je,unregisterTab:Ke,verifyRouteModel:Z,updateModel:le,onKbdNavigate:He,avoidRouteWatcher:!1};ze(Le,me);function ye(){S!==null&&clearTimeout(S),D(),I!==void 0&&I()}let we;return K(ye),nt(()=>{we=I!==void 0,ye()}),ot(()=>{we===!0&&ge(),Y()}),()=>w("div",{ref:P,class:Qe.value,role:"tablist",onFocusin:We,onFocusout:Ne},[w(ne,{onResize:de}),w("div",{ref:d,class:Ee.value,onScroll:N},lt(T.default)),w(G,{class:"q-tabs__arrow q-tabs__arrow--left absolute q-tab__icon"+(E.value===!0?"":" q-tabs__arrow--faded"),name:e.leftIcon||n.iconSet.tabs[e.vertical===!0?"up":"left"],onMousedownPassive:ve,onTouchstartPassive:ve,onMouseupPassive:D,onMouseleavePassive:D,onTouchendPassive:D}),w(G,{class:"q-tabs__arrow q-tabs__arrow--right absolute q-tab__icon"+(A.value===!0?"":" q-tabs__arrow--faded"),name:e.rightIcon||n.iconSet.tabs[e.vertical===!0?"down":"right"],onMousedownPassive:he,onTouchstartPassive:he,onMouseupPassive:D,onMouseleavePassive:D,onTouchendPassive:D})])}}),It=O({name:"QToggle",props:{...St,icon:String,iconColor:String},emits:Ct,setup(e){function T(a,o){const n=f(()=>(a.value===!0?e.checkedIcon:o.value===!0?e.indeterminateIcon:e.uncheckedIcon)||e.icon),g=f(()=>a.value===!0?e.iconColor:null);return()=>[w("div",{class:"q-toggle__track"}),w("div",{class:"q-toggle__thumb absolute flex flex-center no-wrap"},n.value!==void 0?[w(G,{name:n.value,color:g.value})]:void 0)]}return qt("toggle",T)}}),Mt=O({name:"QHeader",props:{modelValue:{type:Boolean,default:!0},reveal:Boolean,revealOffset:{type:Number,default:250},bordered:Boolean,elevated:Boolean,heightHint:{type:[String,Number],default:50}},emits:["reveal","focusin"],setup(e,{slots:T,emit:a}){const{proxy:{$q:o}}=U(),n=Re(Ie,j);if(n===j)return console.error("QHeader needs to be child of QLayout"),j;const g=C(parseInt(e.heightHint,10)),m=C(!0),L=f(()=>e.reveal===!0||n.view.value.indexOf("H")>-1||o.platform.is.ios&&n.isContainer.value===!0),h=f(()=>{if(e.modelValue!==!0)return 0;if(L.value===!0)return m.value===!0?g.value:0;const u=g.value-n.scroll.value.position;return u>0?u:0}),c=f(()=>e.modelValue!==!0||L.value===!0&&m.value!==!0),R=f(()=>e.modelValue===!0&&c.value===!0&&e.reveal===!0),$=f(()=>"q-header q-layout__section--marginal "+(L.value===!0?"fixed":"absolute")+"-top"+(e.bordered===!0?" q-header--bordered":"")+(c.value===!0?" q-header--hidden":"")+(e.modelValue!==!0?" q-layout--prevent-focus":"")),P=f(()=>{const u=n.rows.value.top,i={};return u[0]==="l"&&n.left.space===!0&&(i[o.lang.rtl===!0?"right":"left"]=`${n.left.size}px`),u[2]==="r"&&n.right.space===!0&&(i[o.lang.rtl===!0?"left":"right"]=`${n.right.size}px`),i});function d(u,i){n.update("header",u,i)}function q(u,i){u.value!==i&&(u.value=i)}function B({height:u}){q(g,u),d("size",u)}function E(u){R.value===!0&&q(m,!0),a("focusin",u)}M(()=>e.modelValue,u=>{d("space",u),q(m,!0),n.animate()}),M(h,u=>{d("offset",u)}),M(()=>e.reveal,u=>{u===!1&&q(m,e.modelValue)}),M(m,u=>{n.animate(),a("reveal",u)}),M(n.scroll,u=>{e.reveal===!0&&q(m,u.direction==="up"||u.position<=e.revealOffset||u.position-u.inflectionPoint<100)});const A={};return n.instances.header=A,e.modelValue===!0&&d("size",g.value),d("space",e.modelValue),d("offset",h.value),K(()=>{n.instances.header===A&&(n.instances.header=void 0,d("size",0),d("offset",0),d("space",!1))}),()=>{const u=at(T.default,[]);return e.elevated===!0&&u.push(w("div",{class:"q-layout__shadow absolute-full overflow-hidden no-pointer-events"})),u.push(w(ne,{debounce:0,onResize:B})),w("header",{class:$.value,style:P.value,onFocusin:E},u)}}});const{passive:_e}=ce,Bt=["both","horizontal","vertical"];var At=O({name:"QScrollObserver",props:{axis:{type:String,validator:e=>Bt.includes(e),default:"vertical"},debounce:[String,Number],scrollTarget:{default:void 0}},emits:["scroll"],setup(e,{emit:T}){const a={position:{top:0,left:0},direction:"down",directionChanged:!1,delta:{top:0,left:0},inflectionPoint:{top:0,left:0}};let o=null,n,g;M(()=>e.scrollTarget,()=>{h(),L()});function m(){o!==null&&o();const $=Math.max(0,gt(n)),P=mt(n),d={top:$-a.position.top,left:P-a.position.left};if(e.axis==="vertical"&&d.top===0||e.axis==="horizontal"&&d.left===0)return;const q=Math.abs(d.top)>=Math.abs(d.left)?d.top<0?"up":"down":d.left<0?"left":"right";a.position={top:$,left:P},a.directionChanged=a.direction!==q,a.delta=d,a.directionChanged===!0&&(a.direction=q,a.inflectionPoint=a.position),T("scroll",{...a})}function L(){n=bt(g,e.scrollTarget),n.addEventListener("scroll",c,_e),c(!0)}function h(){n!==void 0&&(n.removeEventListener("scroll",c,_e),n=void 0)}function c($){if($===!0||e.debounce===0||e.debounce==="0")m();else if(o===null){const[P,d]=e.debounce?[setTimeout(m,e.debounce),clearTimeout]:[requestAnimationFrame(m),cancelAnimationFrame];o=()=>{d(P),o=null}}}const{proxy:R}=U();return M(()=>R.$q.lang.rtl,m),p(()=>{g=R.$el.parentNode,L()}),K(()=>{o!==null&&o(),h()}),Object.assign(R,{trigger:c,getPosition:()=>a}),$e}}),Qt=O({name:"QLayout",props:{container:Boolean,view:{type:String,default:"hhh lpr fff",validator:e=>/^(h|l)h(h|r) lpr (f|l)f(f|r)$/.test(e.toLowerCase())},onScroll:Function,onScrollHeight:Function,onResize:Function},setup(e,{slots:T,emit:a}){const{proxy:{$q:o}}=U(),n=C(null),g=C(o.screen.height),m=C(e.container===!0?0:o.screen.width),L=C({position:0,direction:"down",inflectionPoint:0}),h=C(0),c=C(Pe.value===!0?0:se()),R=f(()=>"q-layout q-layout--"+(e.container===!0?"containerized":"standard")),$=f(()=>e.container===!1?{minHeight:o.screen.height+"px"}:null),P=f(()=>c.value!==0?{[o.lang.rtl===!0?"left":"right"]:`${c.value}px`}:null),d=f(()=>c.value!==0?{[o.lang.rtl===!0?"right":"left"]:0,[o.lang.rtl===!0?"left":"right"]:`-${c.value}px`,width:`calc(100% + ${c.value}px)`}:null);function q(r){if(e.container===!0||document.qScrollPrevented!==!0){const b={position:r.position.top,direction:r.direction,directionChanged:r.directionChanged,inflectionPoint:r.inflectionPoint.top,delta:r.delta.top};L.value=b,e.onScroll!==void 0&&a("scroll",b)}}function B(r){const{height:b,width:S}=r;let x=!1;g.value!==b&&(x=!0,g.value=b,e.onScrollHeight!==void 0&&a("scrollHeight",b),A()),m.value!==S&&(x=!0,m.value=S),x===!0&&e.onResize!==void 0&&a("resize",r)}function E({height:r}){h.value!==r&&(h.value=r,A())}function A(){if(e.container===!0){const r=g.value>h.value?se():0;c.value!==r&&(c.value=r)}}let u=null;const i={instances:{},view:f(()=>e.view),isContainer:f(()=>e.container),rootRef:n,height:g,containerHeight:h,scrollbarWidth:c,totalWidth:f(()=>m.value+c.value),rows:f(()=>{const r=e.view.toLowerCase().split(" ");return{top:r[0].split(""),middle:r[1].split(""),bottom:r[2].split("")}}),header:ee({size:0,offset:0,space:!1}),right:ee({size:300,offset:0,space:!1}),footer:ee({size:0,offset:0,space:!1}),left:ee({size:300,offset:0,space:!1}),scroll:L,animate(){u!==null?clearTimeout(u):document.body.classList.add("q-body--layout-animate"),u=setTimeout(()=>{u=null,document.body.classList.remove("q-body--layout-animate")},155)},update(r,b,S){i[r][b]=S}};if(ze(Ie,i),se()>0){let S=function(){r=null,b.classList.remove("hide-scrollbar")},x=function(){if(r===null){if(b.scrollHeight>o.screen.height)return;b.classList.add("hide-scrollbar")}else clearTimeout(r);r=setTimeout(S,300)},I=function(Q){r!==null&&Q==="remove"&&(clearTimeout(r),S()),window[`${Q}EventListener`]("resize",x)},r=null;const b=document.body;M(()=>e.container!==!0?"add":"remove",I),e.container!==!0&&I("add"),it(()=>{I("remove")})}return()=>{const r=xe(T.default,[w(At,{onScroll:q}),w(ne,{onResize:B})]),b=w("div",{class:R.value,style:$.value,ref:e.container===!0?void 0:n,tabindex:-1},r);return e.container===!0?w("div",{class:"q-layout-container overflow-hidden",ref:n},[w(ne,{onResize:E}),w("div",{class:"absolute-full",style:P.value},[w("div",{class:"scroll",style:d.value},[b])])]):b}}});const Et=rt("globalStore",()=>{const e=yt(),T=C(localStorage.getItem("darkMode")!=="false");return e.dark.set(!T.value),M(T,a=>{localStorage.setItem("darkMode",a.toString()),e.dark.set(!T.value)}),{darkMode:T}}),Ot=ut({__name:"MainLayout",setup(e){const T=Et();return(a,o)=>{const n=st("router-view");return ct(),dt(Qt,{view:"hHh lpR fFf"},{default:te(()=>[H(Mt,{class:"bg-primary text-white","height-hint":"98"},{default:te(()=>[H(wt,null,{default:te(()=>[H(zt,{"inline-label":"",align:"left"},{default:te(()=>[H(qe,{to:"/",label:"Vis Publications",icon:"img:logo.svg"}),H(qe,{to:"/about",label:"About"})]),_:1}),H(Tt),H(It,{modelValue:re(T).darkMode,"onUpdate:modelValue":o[0]||(o[0]=g=>re(T).darkMode=g),"checked-icon":"light_mode",color:"yellow-8","unchecked-icon":"dark_mode",title:`Switch to ${re(T).darkMode?"dark":"light"} mode`},null,8,["modelValue","title"]),H(ft,{href:"https://github.com/Dev-Lan/vispubs",target:"_blank",flat:"",round:"",size:"md",icon:"fa-brands fa-github"})]),_:1})]),_:1}),H(n)]),_:1})}}});export{Ot as default};