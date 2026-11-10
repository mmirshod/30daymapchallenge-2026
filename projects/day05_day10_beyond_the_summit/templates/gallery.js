'use strict';
(() => {
  const chooser=document.getElementById('gallery-language');
  let stored;try{stored=localStorage.getItem('bts-language');}catch{}
  const requested=new URLSearchParams(location.search).get('lang');
  let language=['ru','en'].includes(requested)?requested:(stored==='en'?'en':'ru');
  function apply(){document.documentElement.lang=language;chooser.value=language;document.querySelectorAll('[data-ru][data-en]').forEach(el=>el.textContent=el.dataset[language]);try{localStorage.setItem('bts-language',language);}catch{}const url=new URL(location.href);url.searchParams.set('lang',language);history.replaceState(null,'',url);}
  chooser.addEventListener('change',()=>{language=chooser.value;apply();});apply();
  const buttons=document.querySelectorAll('[data-filter]'),cards=[...document.querySelectorAll('.work-card')];
  buttons.forEach(button=>button.addEventListener('click',()=>{buttons.forEach(b=>b.setAttribute('aria-pressed',b===button));const filter=button.dataset.filter;let count=0;cards.forEach(card=>{const show=filter==='all'||(filter==='interactive'?card.dataset.interactive==='1':card.dataset.kind===filter);card.hidden=!show;if(show)count++;});document.getElementById('collection-count').textContent=count+' / '+cards.length;}));
})();
