#!/usr/bin/env python3
"""My Daily Dashboard V2 - standard-library RSS server. Run: python3 server.py"""
import json, os, re, threading, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PORT=int(os.getenv('PORT','8000'))
TOPICS={
 'local':{'all':'الإمارات دبي أخبار','uae':'الإمارات أخبار','dubai':'دبي أخبار','gulf':'الخليج أخبار'},
 'world':{'all':'أهم الأخبار العالمية','us':'أمريكا أخبار','china':'الصين أخبار','europe':'أوروبا أخبار','asia':'آسيا أخبار'},
 'sports':{'all':'أخبار الرياضة','football':'كرة القدم أخبار','f1':'Formula 1 F1 racing news','ufc':'UFC MMA news','cycling':'cycling races news'},
 'cars':{'all':'أخبار السيارات الجديدة','new':'new car launches 2026','sports':'sports cars supercars news','ev':'electric vehicles EV news','china':'Chinese automakers BYD Geely news'},
 'tech':{'all':'أخبار التكنولوجيا الحديثة','apple':'Apple iPhone iOS updates','samsung':'Samsung Galaxy updates','ai':'artificial intelligence AI news','gadgets':'consumer electronics gadgets news'},
 'economy':{'all':'الاقتصاد والأسواق أخبار','gold':'gold silver markets news','oil':'oil prices crude news','stocks':'global stock markets news','currency':'foreign exchange currencies news'},
 'knowledge':{'all':'كتب مقالات بودكاست ثقافة','books':'new books reviews','articles':'science research discoveries','podcasts':'new educational podcasts'}
}
CACHE={}; LOCK=threading.Lock(); TTL=15*60

def get_feed(section, sub, lang):
    if section not in TOPICS or sub not in TOPICS[section] or lang not in ('ar','en'):
        raise ValueError('Invalid category or language')
    key=(section,sub,lang); now=time.time()
    with LOCK:
        cached=CACHE.get(key)
        if cached and now-cached['ts']<TTL: return cached['data']
    q=TOPICS[section][sub]
    if lang=='en':
        en={ 'local':'UAE Dubai latest news','world':'world breaking news','sports':'sports news','cars':'automotive news','tech':'technology news','economy':'business economy news','knowledge':'books research podcasts'}
        if sub=='all':q=en[section]
    hl,gl,ceid=('ar','AE','AE:ar') if lang=='ar' else ('en-US','US','US:en')
    url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':q+' when:3d','hl':hl,'gl':gl,'ceid':ceid})
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; MyDailyDashboard/2.0)'})
    with urllib.request.urlopen(req,timeout=12) as r:
        data=r.read(1_500_000)
    root=ET.fromstring(data)
    articles=[]
    for item in root.findall('./channel/item')[:10]:
        title=(item.findtext('title') or '').strip()
        source=item.find('source')
        src=(source.text or '').strip() if source is not None else ''
        if src and title.endswith(' - '+src):title=title[:-(len(src)+3)]
        link=(item.findtext('link') or '').strip()
        pub=(item.findtext('pubDate') or '').strip()
        if not link.startswith('https://'):continue
        articles.append({'title':title,'source':src or 'Google News','url':link,'published':pub})
    result={'articles':articles,'updated':datetime.now(timezone.utc).isoformat(),'feed':'Google News RSS','category':section,'subcategory':sub,'language':lang}
    with LOCK:CACHE[key]={'ts':now,'data':result}
    return result

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
    def do_GET(self):
        path=urllib.parse.urlsplit(self.path)
        if path.path=='/api/news':
            p=urllib.parse.parse_qs(path.query)
            try:
                result=get_feed(p.get('section',['local'])[0],p.get('sub',['all'])[0],p.get('lang',['ar'])[0]);status=200
            except ValueError as e:result={'error':str(e)};status=400
            except Exception:result={'error':'تعذر جلب الأخبار من المصدر حالياً. حاول مرة أخرى لاحقاً. / News source temporarily unavailable.'};status=503
            blob=json.dumps(result,ensure_ascii=False).encode()
            self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(blob)));self.end_headers();self.wfile.write(blob);return
        if path.path=='/':self.path='/index.html'
        return super().do_GET()

if __name__=='__main__':
    print(f'Open http://localhost:{PORT} in your browser')
    ThreadingHTTPServer(('0.0.0.0',PORT),Handler).serve_forever()
