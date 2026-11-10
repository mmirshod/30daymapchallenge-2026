/* Pure scoring functions, shared by the explorer and browser acceptance checks. */
(function(root){
  'use strict';
  const defaults=[30,25,30,15];
  function normalize(raw){const a=raw.map(Number);if(a.length!==4||a.some(x=>!Number.isFinite(x)||x<0))throw Error('Invalid weights');const sum=a.reduce((x,y)=>x+y,0);return sum?a.map(x=>x/sum):defaults.map(x=>x/100);}
  function score(s,weights,mode,landmarkWeight){const w=normalize(weights);const n=s.components.reduce((v,x,i)=>v+x*w[i],0);return mode==='mps'?n*(1-landmarkWeight)+s.landmark_score*landmarkWeight:n;}
  function rank(summits,weights,mode,lw){return summits.map(s=>({...s,score:score(s,weights,mode,lw)})).sort((a,b)=>b.score-a.score||(a.id<b.id?-1:a.id>b.id?1:0)).map((s,i)=>({...s,current_rank:i+1}));}
  root.BTSScore={normalize,score,rank,defaults};
})(globalThis);
