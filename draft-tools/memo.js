/* 下書きのときだけ使う道具：気になる所メモ。
   ページの場所を押して一言書き、まとめてコピーして渡す。
   メモはこのブラウザの中（localStorage）にだけ残り、ほかの人には見えない。
   本番では draft-tools/ ごと外す。 */
(function(){
  var bar=document.querySelector('.dm-bar'); if(!bar) return;
  var VER=bar.getAttribute('data-version')||'v1';
  var KEY='jase-draft-memo:'+VER;
  var toggle=bar.querySelector('.dm-toggle'), count=bar.querySelector('.dm-count');
  var memos=load(), on=false, bypass=false, hoverEl=null, pending=null;

  function load(){try{return JSON.parse(localStorage.getItem(KEY))||[]}catch(e){return []}}
  function save(){try{localStorage.setItem(KEY,JSON.stringify(memos))}catch(e){}}
  function el(tag,cls,txt){var e=document.createElement(tag); if(cls) e.className=cls; if(txt!=null) e.textContent=txt; return e}

  var panel=el('div','dm-panel dm-ui'); panel.hidden=true;
  panel.setAttribute('role','dialog'); panel.setAttribute('aria-label','気になる所のメモ');
  panel.innerHTML='<p class="dm-h">気になる所のメモ</p>'+
    '<p class="dm-help">ページの気になる所を押すと、そこへのメモを書けます。</p>'+
    '<ol class="dm-list"></ol><p class="dm-done" aria-live="polite"></p>'+
    '<div class="dm-btns"><button type="button" class="dm-copy">まとめてコピー</button>'+
    '<button type="button" class="dm-clear">すべて消す</button>'+
    '<button type="button" class="dm-close">メモを終える</button></div>';
  var list=panel.querySelector('.dm-list'), done=panel.querySelector('.dm-done'), help=panel.querySelector('.dm-help');

  var sheet=el('div','dm-sheet dm-ui'); sheet.hidden=true;
  sheet.setAttribute('role','dialog'); sheet.setAttribute('aria-label','メモを書く');
  sheet.innerHTML='<p class="dm-where"></p>'+
    '<textarea rows="3" aria-label="気になること" placeholder="気になることを一言（例：文字が大きすぎる）"></textarea>'+
    '<div class="dm-btns"><button type="button" class="dm-save">メモする</button>'+
    '<button type="button" class="dm-cancel">やめる</button></div>';
  var where=sheet.querySelector('.dm-where'), ta=sheet.querySelector('textarea');
  document.body.appendChild(panel); document.body.appendChild(sheet);

  function view(){return window.innerWidth<768?'スマホ':'パソコン'}
  function secOf(t){var s=t.closest('[data-sec]'); return s?{id:s.getAttribute('data-sec'),name:s.getAttribute('data-sec-name')}:{id:'-',name:'区画の外'}}
  function what(t){
    var x=t.getAttribute('aria-label')||t.getAttribute('alt')||(t.innerText||'').replace(/\s+/g,' ').trim();
    if(!x) return '文字のない部分';
    return x.length>32?x.slice(0,32)+'…':x;
  }
  // 区画の記号（dm-badge）は数えないので、記号を出していても出していなくても同じ道筋になる
  function pathOf(t){
    var parts=[];
    while(t&&t.nodeType===1&&t!==document.body){
      var i=1,s=t; while((s=s.previousElementSibling)) if(s.tagName===t.tagName) i++;
      parts.unshift(t.tagName.toLowerCase()+':nth-of-type('+i+')'); t=t.parentElement;
    }
    return 'body>'+parts.join('>');
  }
  function find(m){try{return document.querySelector(m.path)}catch(e){return null}}
  function markAll(){memos.forEach(function(m){var t=find(m); if(t) t.classList.add('dm-marked')})}
  function unmarkAll(){document.querySelectorAll('.dm-marked').forEach(function(t){t.classList.remove('dm-marked')})}
  function flash(t){t.classList.add('dm-flash'); setTimeout(function(){t.classList.remove('dm-flash')},1200)}

  function render(){
    count.textContent=memos.length?String(memos.length):'';
    help.hidden=memos.length>0;
    var out=panel.querySelector('.dm-out'); if(out) out.remove();
    list.innerHTML='';
    memos.forEach(function(m,k){
      var li=el('li');
      var go=el('button','dm-go',m.sec+' '+m.name+'「'+m.what+'」'); go.type='button';
      go.addEventListener('click',function(){var t=find(m); if(t){t.scrollIntoView({behavior:'smooth',block:'center'}); flash(t)}});
      var del=el('button','dm-del','消す'); del.type='button'; del.setAttribute('aria-label',(k+1)+'番目のメモを消す');
      del.addEventListener('click',function(){memos.splice(k,1); save(); unmarkAll(); markAll(); render()});
      li.appendChild(go); li.appendChild(el('span','dm-text',m.text+'（'+m.view+'）')); li.appendChild(del);
      list.appendChild(li);
    });
  }

  function badges(show){
    document.querySelectorAll('dm-badge').forEach(function(b){b.remove()});
    if(!show) return;
    document.querySelectorAll('[data-sec]').forEach(function(s){
      var b=document.createElement('dm-badge'); b.className='dm-ui';
      b.appendChild(el('b','',s.getAttribute('data-sec')));
      b.appendChild(el('span','',' '+s.getAttribute('data-sec-name')));
      s.insertBefore(b,s.firstChild);
    });
  }
  function pauseCarousel(){
    var pb=document.querySelector('.car .pause');
    if(pb&&pb.textContent!=='▶'){bypass=true; pb.click(); bypass=false}
  }
  function setOn(v){
    on=v; document.body.classList.toggle('dm-on',on);
    toggle.setAttribute('aria-pressed',on?'true':'false');
    if(!on) closeSheet();
    panel.hidden=!on; done.textContent='';
    badges(on);
    if(on) pauseCarousel();
  }

  function openSheet(t){
    var s=secOf(t);
    pending={sec:s.id,name:s.name,what:what(t),path:pathOf(t)};
    where.textContent=s.id+' '+s.name+'　「'+pending.what+'」';
    ta.value=''; sheet.hidden=false; panel.hidden=true;
    if(hoverEl) hoverEl.classList.remove('dm-hover');
    hoverEl=t; t.classList.add('dm-hover');
    ta.focus();
  }
  function closeSheet(){
    sheet.hidden=true; pending=null;
    if(hoverEl){hoverEl.classList.remove('dm-hover'); hoverEl=null}
    if(on) panel.hidden=false;
  }
  function saveMemo(){
    var v=ta.value.trim(); if(!v||!pending){ta.focus(); return}
    pending.text=v; pending.view=view(); pending.w=window.innerWidth;
    memos.push(pending); save(); markAll(); closeSheet(); render();
  }
  function memoText(){
    var url=location.href.split('#')[0].split('?')[0];
    var lines=['デザイン案 '+VER+' の気になる所（'+memos.length+'件）'];
    memos.forEach(function(m,k){lines.push((k+1)+'. 【'+m.sec+' '+m.name+'】「'+m.what+'」 '+m.text+'（'+m.view+' '+m.w+'px）')});
    lines.push('ページ：'+url);
    return lines.join('\n');
  }
  function copy(){
    if(!memos.length){done.textContent='まだメモがありません。'; return}
    var s=memoText();
    var out=panel.querySelector('.dm-out'); if(out) out.remove();
    function ok(){done.textContent='コピーしました。Claude Code やLINEにそのまま貼ってください。'}
    // 自動でコピーできないときは、文をそのまま見せて手でコピーしてもらう
    function manual(){
      done.textContent='自動でコピーできませんでした。下の文を選んでコピーしてください。';
      var a=el('textarea','dm-out'); a.value=s; a.readOnly=true; a.rows=5;
      panel.insertBefore(a,panel.querySelector('.dm-btns')); a.focus(); a.select();
    }
    function fallback(){
      var a=document.createElement('textarea'); a.value=s; a.setAttribute('readonly','');
      a.style.position='fixed'; a.style.opacity='0'; document.body.appendChild(a); a.select();
      var done1=false; try{done1=document.execCommand('copy')}catch(e){}
      a.remove(); done1?ok():manual();
    }
    if(navigator.clipboard&&window.isSecureContext) navigator.clipboard.writeText(s).then(ok,fallback); else fallback();
  }

  document.addEventListener('click',function(e){
    if(!on||bypass) return;
    var t=e.target; if(!(t instanceof Element)||t.closest('.dm-ui')) return;
    e.preventDefault(); e.stopPropagation();
    openSheet(t);
  },true);
  document.addEventListener('mouseover',function(e){
    if(!on||!sheet.hidden) return;
    var t=e.target; if(!(t instanceof Element)||t.closest('.dm-ui')) return;
    if(hoverEl) hoverEl.classList.remove('dm-hover');
    hoverEl=t; t.classList.add('dm-hover');
  });
  toggle.addEventListener('click',function(){setOn(!on)});
  panel.querySelector('.dm-copy').addEventListener('click',copy);
  panel.querySelector('.dm-clear').addEventListener('click',function(){
    if(!memos.length) return;
    if(!window.confirm('メモを'+memos.length+'件とも消します。よいですか？')) return;
    memos=[]; save(); unmarkAll(); render(); done.textContent='';
  });
  panel.querySelector('.dm-close').addEventListener('click',function(){setOn(false)});
  sheet.querySelector('.dm-save').addEventListener('click',saveMemo);
  sheet.querySelector('.dm-cancel').addEventListener('click',closeSheet);
  ta.addEventListener('keydown',function(e){
    if(e.key==='Enter'&&(e.metaKey||e.ctrlKey)) saveMemo();
    if(e.key==='Escape') closeSheet();
  });

  markAll(); render();
  if(/[?&]memo\b/.test(location.search)) setOn(true);
})();
