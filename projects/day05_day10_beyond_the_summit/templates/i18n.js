/* Optional Russian presentation layer. Data IDs, option values and scores stay unchanged. */
(function(){
  'use strict';
  const ru={
    'Current leader':'Лидер режима','Highlight Top 10':'Выделить Top 10',
    'Selected summit':'Выбранная вершина','Mode leader':'Лидер режима',
    'Leaders use the full cohort and current weights.':'Лидеры по всей выборке с текущими весами.',
    'Skip to explorer':'Перейти к карте',
    'DAY 05 · SIGHT / DAY 10 · PROMPTING ONLY':'ДЕНЬ 05 · ВИД / ДЕНЬ 10 · ТОЛЬКО ПРОМПТЫ',
    'Read the method ↗':'О методике ↗',
    'TASHKENT REGION · WESTERN TIEN SHAN':'ТАШКЕНТСКАЯ ОБЛАСТЬ · ЗАПАДНЫЙ ТЯНЬ-ШАНЬ',
    'Beyond':'За пределами','the Summit':'вершины',
    "The highest mountain isn't always the best viewpoint.":'Самая высокая гора — не всегда лучшая обзорная точка.',
    'Explore the terrain. Change the weights. Find your panorama.':'Изучайте рельеф. Меняйте веса. Найдите свою панораму.',
    'summits above 1,800 m':'вершины выше 1 800 м','100 km':'100 км','30 m':'30 м',
    'visibility radius':'радиус видимости','terrain model':'модель рельефа','Horizon landmarks':'объектов «Горизонта»',
    'Download the Day 05 report ↓':'Скачать отчёт Day 05 (EN) ↓',
    'Mountain panorama explorer':'Атлас горных панорам','Ranking mode':'Вид рейтинга',
    'Natural':'Природный','Mountaineering':'Альпинистский','Published weights':'Исходные веса',
    'Your weights · exploratory ranking':'Ваши веса · экспериментальный рейтинг',
    'Reset weights':'Сбросить веса','Copy this view':'Скопировать ссылку','Link copied':'Ссылка скопирована',
    'What makes a view?':'Из чего складывается вид?',
    'Set relative importance. The four weights are normalized to 100%.':'Задайте относительную важность. Четыре веса приводятся к сумме 100%.',
    'Terrain':'Рельеф','Visible peaks':'Видимые вершины','Skyline':'Горизонт','Distance':'Дальность',
    'terrain':'рельеф','peaks':'вершины','skyline':'горизонт','distance':'дальность','Horizon L':'«Горизонт» L',
    'Landmarks in MPS':'Доля объектов в MPS',
    'All weights are zero: published NPS weights are used.':'Все веса равны нулю: используются исходные веса NPS.',
    'Find a summit':'Найти вершину','Name or OSM ID':'Название или OSM ID',
    'Elevation band':'Высотный диапазон','All elevations':'Все высоты','Horizon visibility':'Видимость «Горизонта»',
    'All summits':'Все вершины','At least one Horizon summit':'Хотя бы одна вершина «Горизонта»',
    'Download this ranking · CSV':'Скачать этот рейтинг · CSV','Special viewpoints':'Особые обзорные точки',
    'Lower score':'Ниже оценка','Higher score':'Выше оценка','Terrain backdrop · Copernicus DEM':'Рельеф · Copernicus DEM',
    'Your ranking':'Ваш рейтинг',
    'Select a row or a map point to inspect a summit. Ranks use the full cohort; band ranks use your selected elevation band.':'Выберите строку или точку на карте. Общие места рассчитаны по всем вершинам; места по высоте — внутри соответствующего диапазона.',
    'Rank':'Место','Summit':'Вершина','m':'м','Score':'Оценка','Band rank':'По высоте',
    'Select a summit to see its panorama.':'Выберите вершину, чтобы увидеть её панораму.',
    'Score / 100':'Баллы / 100','Summit elevation':'Высота вершины',
    'Highest distance uses a geodesic measurement inside the projected 100 km mask. Ground-cell visibility is not field-confirmed recognition.':'Максимальная дальность измерена по геодезической внутри проекционной маски 100 км. Видимость ячейки поверхности не означает подтверждённого распознавания вершины.',
    'Skyline · true azimuth':'Линия горизонта · истинный азимут','Loading profile…':'Загрузка профиля…',
    'Show visible connections':'Показать линии видимости','Horizon only':'Только «Горизонт»',
    'none':'нет','Skyline elevation angle in degrees across true azimuth':'Угол линии горизонта в градусах по истинному азимуту',
    'HOW TO READ THE LANDSCAPE':'КАК ЧИТАТЬ ЛАНДШАФТ','A model of a view.':'Модель горного вида.',
    'A starting point for exploration.':'Отправная точка для исследования.',
    'Natural Panorama Score':'Оценка природной панорамы · NPS',
    'The published NPS combines terrain (30%), visible peak proxies (25%), skyline (30%) and distance (15%). Components use cohort-relative percentiles and documented physical summaries, each on a 0–100 scale.':'Исходный NPS объединяет рельеф (30%), видимость точек вершин (25%), линию горизонта (30%) и дальность (15%). Компоненты используют процентили внутри выборки и описанные характеристики рельефа по шкале 0–100.',
    'Changing the sliders recombines these precomputed components. It does not recalculate terrain visibility, normalization, or the internal definitions of the components.':'Ползунки меняют сочетание готовых компонентов. Видимость рельефа, нормализация и внутренние формулы компонентов не пересчитываются.',
    'Mountaineering Panorama Score':'Оценка альпинистской панорамы · MPS',
    'Published MPS = 80% NPS + 20% L. Horizon-only L combines visible landmark coverage (70%), distance (15%) and clipped positive angular relief (15%), with the same denominator of 15 for every observer. Self-observation is excluded.':'Исходный MPS = 80% NPS + 20% L. Компонент L программы «Горизонт» объединяет долю видимых объектов (70%), дальность (15%) и ограниченную положительную угловую высоту (15%). Знаменатель для всех наблюдателей равен 15. Видимость самой себя исключена.',
    'Only Horizon is in scope. Mirage, Cascade and Underground are excluded. All five supplied Snow Leopard targets lie beyond 100 km. Program breadth is therefore omitted.':'Учитывается только «Горизонт». «Мираж», «Каскад» и «Подземелье» исключены. Все пять указанных объектов «Снежного барса» находятся дальше 100 км. Разнообразие программ в оценке не учитывается.',
    'Know the limits':'Ограничения модели',
    'GDAL ground-target viewsheds on a 30 m Copernicus surface model are exploratory. A visible raster cell is not confirmed recognition of a summit. Vegetation, clouds and local terrain may change the real view. Skyline angular contrast is not topographic prominence.':'Зоны видимости GDAL по 30-метровой модели поверхности Copernicus носят экспериментальный характер. Видимая ячейка растра не гарантирует распознавания вершины. Растительность, облака и локальный рельеф меняют реальный вид. Угловой контраст линии горизонта не равен относительной высоте вершины.',
    'The 100 km limit is projected; edge distances can slightly exceed 100 km geodesically. Elevation correlation is descriptive (Spearman 0.329), not causal. Nearly tied winners change with weights.':'Ограничение 100 км задано в проекции; геодезические расстояния на границе могут немного превышать 100 км. Корреляция с высотой описательная (Спирмен: 0,329), без причинного вывода. Близкие по баллам лидеры меняются при изменении весов.',
    'Profiles are displayed at 1° intervals, sampled from the original 0.1° calculations. Visible connections refer to DEM-ground point proxies. No weather or field visibility is implied.':'Профили показаны с шагом 1° из исходных расчётов с шагом 0,1°. Линии видимости относятся к точкам поверхности DEM. Погода и фактическая видимость на местности не моделируются.',
    'Day 05 · 3-page PDF ↓':'Day 05 · PDF, 3 страницы (EN) ↓',
    'Day 10 · 3-page PDF ↓':'Day 10 · PDF, 3 страницы (EN) ↓',
    'Published rankings · CSV ↓':'Исходные рейтинги · CSV ↓','Full methodology ↓':'Полная методика (EN) ↓',
    'Data provenance ↓':'Происхождение данных ↓','Sources:':'Источники:',
    '(target snapshot 2026-11-02);':'(снимок целей от 2026-11-02);',
    '. Original map data and derived visibility results retain their source attribution. Leaflet 1.9.4 · BSD-2-Clause. Built entirely through code with Python and Codex.':'. Исходные картографические данные и производные результаты сохраняют указание источников. Leaflet 1.9.4 · BSD-2-Clause. Всё создано программно с помощью Python и Codex.',
    '30DayMapChallenge 2026 · Days 05 + 10':'30DayMapChallenge 2026 · Дни 05 + 10',
    'Back to the mountains ↑':'Вернуться к горам ↑',
    'largest visible area ↗':'Максимальная видимая площадь ↗','most visible peaks ↗':'Больше всего видимых вершин ↗',
    'highest skyline component ↗':'Наивысшая оценка горизонта ↗','farthest visible peak proxy ↗':'Самая дальняя видимая точка вершины ↗',
    'best below 2500m ↗':'Лучший вид ниже 2 500 м ↗'
  };
  let saved;try{saved=localStorage.getItem('bts-language');}catch{}
  const query=new URLSearchParams(location.search).get('lang');
  let lang=(query==='ru'||query==='en')?query:(saved==='ru'?'ru':'en');
  const originals=new WeakMap();const attributes=new WeakMap();
  function text(value){
    const core=value.trim().replace(/\u00a0/g,' '),trimmed=core.replace(/\s+/g,' ');
    let result=ru[core]??ru[trimmed];
    if(result===undefined){
      result=core
        .replace(/^Selected summit: /,'Выбранная вершина: ')
        .replace(/^(\d+) of 1,302 summits$/,'$1 из 1 302 вершин')
        .replace(/^NATURAL · PUBLISHED WEIGHTS$/,'ПРИРОДНЫЙ · ИСХОДНЫЕ ВЕСА')
        .replace(/^NATURAL · YOUR WEIGHTS$/,'ПРИРОДНЫЙ · ВАШИ ВЕСА')
        .replace(/^MOUNTAINEERING · PUBLISHED WEIGHTS$/,'АЛЬПИНИСТСКИЙ · ИСХОДНЫЕ ВЕСА')
        .replace(/^MOUNTAINEERING · YOUR WEIGHTS$/,'АЛЬПИНИСТСКИЙ · ВАШИ ВЕСА')
        .replace(/^Overall · band #/,'Общее · по высоте #')
        .replace(/Published NPS #/g,'Исходный NPS #')
        .replace(/visible peak proxies/g,'видимых точек вершин')
        .replace(/visible terrain/g,'видимого рельефа')
        .replace(/Horizon summits/g,'вершин «Горизонта»')
        .replace(/farthest visible peak proxy/g,'максимальная дальность видимой точки вершины')
        .replace(/Skyline component/g,'Компонент горизонта')
        .replace(/local angular contrast/g,'суммарный угловой контраст')
        .replace(/visible connections available/g,'доступных линий видимости')
        .replace(/shown on map/g,'показаны на карте')
        .replace(/^Visible Horizon: /,'Видимые объекты «Горизонта»: ')
        .replace(/: none$/,': нет')
        .replace(/Profile unavailable\./g,'Профиль недоступен.')
        .replace(/km²/g,'км²').replace(/\bkm\b/g,'км')
        .replace(/(\d) m\b/g,'$1 м');
    }
    return value.replace(value.trim(),result);
  }
  function apply(){
    document.documentElement.lang=lang;
    document.title=lang==='ru'?'Beyond the Summit — Атлас горных панорам':'Beyond the Summit — Mountain Panorama Explorer';
    const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
    let node;while((node=walker.nextNode())){
      if(node.parentElement.closest('script,style,#language'))continue;
      const prior=originals.get(node);const source=prior&&node.data===prior.rendered?prior.source:node.data;
      const rendered=lang==='ru'?text(source):source;
      originals.set(node,{source,rendered});if(node.data!==rendered)node.data=rendered;
    }
    document.querySelectorAll('[placeholder],[aria-label]').forEach(el=>{
      if(el.id==='language')return;
      const cache=attributes.get(el)||{};
      for(const key of ['placeholder','aria-label'])if(el.hasAttribute(key)){
        const value=el.getAttribute(key),prior=cache[key],source=prior&&value===prior.rendered?prior.source:value;
        const rendered=lang==='ru'?text(source):source;cache[key]={source,rendered};if(value!==rendered)el.setAttribute(key,rendered);
      }attributes.set(el,cache);
    });
  }
  let queued=false;
  const observer=new MutationObserver(()=>{if(!queued){queued=true;queueMicrotask(()=>{queued=false;apply();});}});
  function setLanguage(value){
    lang=value==='ru'?'ru':'en';try{localStorage.setItem('bts-language',lang);}catch{}
    const url=new URL(location.href);url.searchParams.set('lang',lang);history.replaceState(null,'',url);
    document.getElementById('language').value=lang;apply();
  }
  document.getElementById('language').value=lang;
  document.getElementById('language').addEventListener('change',event=>setLanguage(event.target.value));
  apply();observer.observe(document.body,{subtree:true,childList:true,characterData:true});
  window.BTSI18n={get language(){return lang;},apply};
})();
