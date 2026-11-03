/* サイト全体で使う小さな動き。外のライブラリは使わない */

// スマホのメニューを開く・閉じる
(function(){
  var hd=document.querySelector('.hd'), mb=document.querySelector('.menu-btn'); if(!hd||!mb) return;
  mb.addEventListener('click',function(){var o=hd.classList.toggle('open');mb.setAttribute('aria-expanded',o?'true':'false');mb.setAttribute('aria-label',o?'メニューを閉じる':'メニューを開く')});
})();

// ロゴの帯が見えなくなったら、メニューの帯の左に小さな紋章を出す
(function(){
  var b=document.querySelector('.banner'), hd=document.querySelector('.hd'); if(!b||!hd||!('IntersectionObserver' in window)) return;
  new IntersectionObserver(function(es){hd.classList.toggle('stuck',!es[0].isIntersecting)}).observe(b);
})();

// トップのカルーセル
(function(){
  var car=document.querySelector('.car'); if(!car) return;
  var track=car.querySelector('.track'), slides=car.querySelectorAll('.slide'), dots=car.querySelectorAll('.dots button');
  var i=0, timer=null, reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function go(n){
    i=(n+slides.length)%slides.length;
    track.style.transform='translateX('+(-100*i)+'%)';
    dots.forEach(function(d,k){d.setAttribute('aria-current',k===i?'true':'false')});
    slides.forEach(function(s,k){s.setAttribute('aria-hidden',k===i?'false':'true')});
  }
  function start(){ if(!reduce){ stop(); timer=setInterval(function(){go(i+1)},6000);} }
  function stop(){ if(timer){clearInterval(timer);timer=null;} }
  car.querySelector('.next').addEventListener('click',function(){go(i+1);start()});
  car.querySelector('.prev').addEventListener('click',function(){go(i-1);start()});
  dots.forEach(function(d,k){d.addEventListener('click',function(){go(k);start()})});
  var pb=car.querySelector('.pause'), paused=false;
  pb.addEventListener('click',function(){paused=!paused; if(paused){stop();pb.textContent='▶';pb.setAttribute('aria-label','自動の切りかえを再開する')}else{start();pb.textContent='Ⅱ';pb.setAttribute('aria-label','自動の切りかえを止める')}});
  var _start=start; start=function(){ if(!paused) _start(); };
  car.addEventListener('mouseenter',stop); car.addEventListener('mouseleave',start);
  car.addEventListener('focusin',stop); car.addEventListener('focusout',start);
  go(0); start();
})();

// お知らせの一覧を、ラベルと年でしぼる
(function(){
  var box=document.querySelector('.filter'); if(!box) return;
  var items=document.querySelectorAll('.news-list.all a'), chips=box.querySelectorAll('.chips button');
  var sel=box.querySelector('select'), count=box.querySelector('.count'), empty=document.querySelector('.news-empty');
  var kind='all', year='all';
  function apply(){
    var n=0;
    items.forEach(function(a){
      var ok=(kind==='all'||a.getAttribute('data-kind')===kind)&&(year==='all'||a.getAttribute('data-year')===year);
      a.hidden=!ok; if(ok) n++;
    });
    count.textContent=n+'件';
    if(empty) empty.hidden=n>0;
  }
  chips.forEach(function(b){b.addEventListener('click',function(){
    kind=b.getAttribute('data-kind');
    chips.forEach(function(c){c.setAttribute('aria-pressed',c===b?'true':'false')});
    apply();
  })});
  sel.addEventListener('change',function(){year=sel.value; apply()});
  apply();
})();
