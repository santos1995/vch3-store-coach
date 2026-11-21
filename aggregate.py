# Run: python3 aggregate.py /path/to/private-pack/csv > data.js
# Raw customer IDs remain local and are never serialized.
import csv, json, statistics
from collections import defaultdict
from datetime import date, timedelta

import sys, pathlib
CSV = str(pathlib.Path(sys.argv[1])) + '/'  # private pack CSV directory supplied by the operator
END = date(2026, 10, 31)
RECENT = (date(2026, 10, 4), END)      # last 28 days
PRIOR = (date(2026, 9, 6), date(2026, 10, 3))
ATTACH = {'Safa', 'Mojari', 'Mala'}

def rd(name):
    with open(CSV + name + '.csv') as f:
        yield from csv.DictReader(f)

stores = {r['store_id']: r for r in rd('stores')}
ams = {r['area_manager_id']: {'name': r['name'], 'city': r['city'],
       'stores': [s.strip() for s in r['stores'].split(',')]} for r in rd('area_managers')}
sps = {r['salesperson_id']: r for r in rd('salespeople')}
items = {r['sku_id']: r for r in rd('items')}
cal = {}
for r in rd('calendar'):
    cal[(r['date'], r['state'])] = r
roster = defaultdict(lambda: defaultdict(int))      # store -> date -> present
sp_present = defaultdict(lambda: defaultdict(int))  # sp -> period 'r'/'p' -> days
sp_off = defaultdict(int)                            # sp -> Off days in RECENT
sp_last = {}                                         # sp -> last Present date
sp_days = defaultdict(set)                           # sp -> set of Present dates
for r in rd('roster_daily'):
    d = date.fromisoformat(r['date'])
    if r['status'] == 'Present':
        roster[r['store_id']][r['date']] += 1
        sp_last[r['salesperson_id']] = max(d, sp_last.get(r['salesperson_id'], d))
        sp_days[r['salesperson_id']].add(d)
        if RECENT[0] <= d <= RECENT[1]: sp_present[r['salesperson_id']]['r'] += 1
        elif PRIOR[0] <= d <= PRIOR[1]: sp_present[r['salesperson_id']]['p'] += 1
    elif r['status'] == 'Off' and RECENT[0] <= d <= RECENT[1]:
        sp_off[r['salesperson_id']] += 1
foot = defaultdict(dict)
for r in rd('footfall_daily'):
    foot[r['store_id']][r['date']] = int(r['footfall'])

bills = {}
sp_bill_days = defaultdict(lambda: defaultdict(int))  # sp -> date -> bills
for r in rd('bills'):
    bills[r['bill_id']] = (date.fromisoformat(r['bill_date']), r['store_id'], r['salesperson_id'], r['customer_id'])
    sp_bill_days[r['salesperson_id']][date.fromisoformat(r['bill_date'])] += 1

# per-bill line aggregates
bl = defaultdict(lambda: {'qty': 0, 'rev': 0.0, 'disc': 0.0, 'cats': set()})
bad_lines = 0
for r in rd('bill_lines'):
    it = items.get(r['sku_id'])
    if it is None or it['is_packaging'] == '1':
        continue
    qty = int(r['qty']); mrp = float(r['mrp']); sp_ = float(r['selling_price'])
    if qty <= 0 or sp_ < 0 or sp_ > mrp:
        bad_lines += 1
    b = bl[r['bill_id']]
    b['qty'] += qty; b['rev'] += qty * sp_; b['disc'] += (mrp - sp_) * qty
    b['cats'].add(it['category'])

def inper(d, p): return p[0] <= d <= p[1]

st = {sid: {'r': defaultdict(float), 'p': defaultdict(float)} for sid in stores}
spm = defaultdict(lambda: defaultdict(float))
spm_p = defaultdict(lambda: defaultdict(float))     # sp -> PRIOR window bill metrics
sp_cat = defaultdict(lambda: defaultdict(int))      # sp -> RECENT bills containing category
CATS = ['Sherwani', 'Kurta Set', 'Indo-Western', 'Jacket', 'Mojari']
cust_first = {}; cust_return = defaultdict(set)     # store -> customers returned 30+ d
cust_seen_store = defaultdict(dict)                 # store -> cust -> first date
for bid, (d, sid, spid, cid) in bills.items():
    l = bl.get(bid)
    att = 1 if (l and ('Sherwani' in l['cats']) and l['cats'] & ATTACH) else 0
    sher = 1 if (l and 'Sherwani' in l['cats']) else 0
    kur = 1 if (l and 'Kurta Set' in l['cats']) else 0
    jack = 1 if (l and kur and 'Jacket' in l['cats']) else 0
    for per, key in ((RECENT, 'r'), (PRIOR, 'p')):
        if inper(d, per):
            s = st[sid][key]
            s['bills'] += 1
            if l:
                s['qty'] += l['qty']; s['rev'] += l['rev']; s['disc'] += l['disc']
                s['sher'] += sher; s['att'] += att; s['kur'] += kur; s['jack'] += jack
            if inper(d, RECENT) or inper(d, PRIOR):
                m = spm[spid]
                if key == 'r':
                    m['bills'] += 1
                    if l:
                        m['qty'] += l['qty']; m['rev'] += l['rev']; m['disc'] += l['disc']
                        m['sher'] += sher; m['att'] += att; m['kur'] += kur; m['jack'] += jack
                        for cname in l['cats']:
                            if cname in CATS: sp_cat[spid][cname] += 1
                else:
                    pp = spm_p[spid]
                    pp['bills'] += 1
                    if l: pp['qty'] += l['qty']; pp['rev'] += l['rev']
    # repeat tracking (all-time, per store)
    fs = cust_seen_store[sid]
    if cid not in fs:
        fs[cid] = d
    else:
        if (d - fs[cid]).days >= 30:
            cust_return[sid].add(cid)

for sid in stores:
    for key, per in (('r', RECENT), ('p', PRIOR)):
        s = st[sid][key]
        s['foot'] = sum(v for dt, v in foot[sid].items() if inper(date.fromisoformat(dt), per))

out = {'data_as_of': END.isoformat(), 'generated_for': 'VCH3 Store Coach demo',
       'notes': 'All data synthetic, from the hackathon data pack. Snapshot date is 31 Oct 2026, not the real current date.',
       'managers': [], 'stores': {}}

def g(sid, key, m): return st[sid][key][m]

city_peers = defaultdict(list)
for sid, s in stores.items():
    city_peers[s['city']].append(sid)

dq_global = {'lines_with_bad_numbers': bad_lines}

for sid, s in stores.items():
    r_, p_ = st[sid]['r'], st[sid]['p']
    conv = r_['bills'] / r_['foot'] if r_['foot'] else None
    convp = p_['bills'] / p_['foot'] if p_['foot'] else None
    ipb = r_['qty'] / r_['bills'] if r_['bills'] else None
    peers = [x for x in city_peers[s['city']] if x != sid]
    pconv = [st[x]['r']['bills'] / st[x]['r']['foot'] for x in peers if st[x]['r']['foot']]
    pipb = [st[x]['r']['qty'] / st[x]['r']['bills'] for x in peers if st[x]['r']['bills']]
    base = cust_seen_store[sid]
    eligible = [c for c, d0 in base.items() if (END - d0).days >= 30]
    rep = len(cust_return[sid] & set(eligible)) / len(eligible) if eligible else None
    prep = []
    for x in peers:
        b2 = cust_seen_store[x]
        el2 = [c for c, d0 in b2.items() if (END - d0).days >= 30]
        if el2:
            prep.append(len(cust_return[x] & set(el2)) / len(el2))
    # understaffed busy days in RECENT
    fl = [(dt, v) for dt, v in foot[sid].items() if inper(date.fromisoformat(dt), RECENT)]
    presents = [roster[sid].get(dt, 0) for dt, _ in fl]
    busy_cut = statistics.quantiles([v for _, v in fl], n=4)[2] if len(fl) >= 4 else None
    med_pres = statistics.median(presents) if presents else 0
    understaffed = sorted(dt for dt, v in fl if busy_cut and v >= busy_cut and roster[sid].get(dt, 0) < med_pres)
    # festival/wedding context next 7 days from END (state-level)
    upcoming = []
    for i in range(1, 8):
        d2 = (END + timedelta(days=i)).isoformat()
        c = cal.get((d2, s['state']))
        if c and (c['festival'] or c['is_wedding_date'] == '1'):
            upcoming.append({'date': d2, 'festival': c['festival'] or None, 'wedding': c['is_wedding_date'] == '1'})
    out['stores'][sid] = {
        'city': s['city'], 'state': s['state'], 'zone': s['zone'], 'tier': s['tier'],
        'am': s['area_manager_id'],
        'conv': conv, 'conv_prior': convp, 'conv_peers': (sum(pconv) / len(pconv)) if pconv else None,
        'ipb': ipb, 'ipb_peers': (sum(pipb) / len(pipb)) if pipb else None,
        'repeat30': rep, 'repeat30_peers': (sum(prep) / len(prep)) if prep else None,
        'rev28': r_['rev'], 'bills28': r_['bills'], 'foot28': r_['foot'],
        'attach_rate': (r_['att'] / r_['sher']) if r_['sher'] else None,
        'jacket_rate': (r_['jack'] / r_['kur']) if r_['kur'] else None,
        'understaffed_busy_days': understaffed,
        'upcoming': upcoming,
    }

# salespeople active in RECENT
for spid, m in spm.items():
    info = sps.get(spid)
    if not info or sp_present[spid]['r'] == 0:
        continue
    sid = info['store_id']
    days = sp_present[spid]['r']
    rec = {'id': spid, 'name': info['name'], 'store': sid, 'days_worked': days,
           'bills': m['bills'], 'bpd': m['bills'] / days,
           'ipb': (m['qty'] / m['bills']) if m['bills'] else None,
           'disc_pct': (m['disc'] / (m['rev'] + m['disc']) * 100) if (m['rev'] + m['disc']) else 0,
           'attach_rate': (m['att'] / m['sher']) if m['sher'] else None,
           'jacket_rate': (m['jack'] / m['kur']) if m['kur'] else None}
    out['stores'][sid].setdefault('team', []).append(rec)

# category shares, strong-absent and frequently-Off detection per store
for sid, s in out['stores'].items():
    team = s.get('team', [])
    elig = [t for t in team if t['days_worked'] >= 7 and t['bills'] >= 10]
    med_bpd = statistics.median([t['bpd'] for t in elig]) if elig else None
    for t in team:
        b = spm[t['id']]['bills']
        t['cat'] = {c: sp_cat[t['id']][c] / b for c in CATS} if b else {}
    absent = []
    missing = []
    for spid, info in sps.items():
        if info['store_id'] != sid:
            continue
        pr = sp_present[spid]['p']; rc = sp_present[spid]['r']
        lp = sp_last.get(spid)
        if lp and END - timedelta(days=60) <= lp <= END - timedelta(days=14):
            w0 = lp - timedelta(days=90)
            pd90 = len([d for d in sp_days[spid] if w0 <= d <= lp])
            bl90 = sum(v for d, v in sp_bill_days[spid].items() if w0 <= d <= lp)
            if pd90 >= 30 and bl90 >= 40:
                bpd_p = bl90 / pd90
                if med_bpd is None or bpd_p >= 0.9 * med_bpd:
                    absent.append({'id': spid, 'name': info['name'],
                                   'last_present': lp.isoformat(),
                                   'bpd_prior': bpd_p, 'bills_prior': int(bl90)})
        elif rc >= 7 and sp_off[spid] >= 8:
            off_counts = [sp_off[p] for p, i2 in sps.items()
                          if i2['store_id'] == sid and sp_present[p]['r'] > 0]
            med_off = statistics.median(off_counts) if off_counts else 0
            bpd = spm[spid]['bills'] / rc
            if sp_off[spid] >= med_off + 2.5 and med_bpd is not None and bpd >= med_bpd:
                missing.append({'id': spid, 'name': info['name'], 'off': sp_off[spid],
                                'off_med': med_off, 'bpd_med': med_bpd,
                                'present': rc, 'bpd': bpd})
    s['absent_strong'] = absent
    s['missing_shifts'] = missing

# city-median category shares among eligible salespeople
city_cat_med = {}
for city, sids in city_peers.items():
    pool = []
    for sid in sids:
        for t in out['stores'][sid].get('team', []):
            if t['days_worked'] >= 7 and t['bills'] >= 10 and t.get('cat'):
                pool.append(t['cat'])
    city_cat_med[city] = {c: (statistics.median([p[c] for p in pool if c in p]) if [p[c] for p in pool if c in p] else None) for c in CATS}
for sid, s in out['stores'].items():
    s['city_cat'] = city_cat_med[s['city']]

for am_id, am in ams.items():
    out['managers'].append({'id': am_id, 'name': am['name'], 'city': am['city'], 'stores': am['stores']})


# Recompute customer cohorts in date order, independent of CSV ordering.
first_store=defaultdict(dict); returned_store=defaultdict(set)
first_sp=defaultdict(dict); returned_sp=defaultdict(set)
daily_bills=defaultdict(lambda:defaultdict(int)); dq=defaultdict(set)
normal=defaultdict(lambda:defaultdict(float)); weekly=defaultdict(lambda:defaultdict(lambda:defaultdict(float)))
normalp=defaultdict(lambda:defaultdict(float))
def special(sid,d):
 c=cal.get((d.isoformat(),stores[sid]['state']))
 return bool(c and (c['festival'].strip() or c['is_wedding_date']=='1'))
for bid,(d,sid,spid,cid) in sorted(bills.items(),key=lambda x:x[1][0]):
 for first,returned,key in [(first_store,returned_store,sid),(first_sp,returned_sp,spid)]:
  f=first[key].setdefault(cid,d)
  if (d-f).days>=30:returned[key].add(cid)
 if inper(d,RECENT):
  daily_bills[sid][d.isoformat()]+=1
  if not special(sid,d):
   normal[sid]['bills']+=1
   normal[sid]['qty']+=bl.get(bid,{}).get('qty',0)
   normal[sid]['rev']+=bl.get(bid,{}).get('rev',0)
 if date(2026,10,18)<=d<=END and not special(sid,d):
  key='before' if d<date(2026,10,25) else 'after'
  weekly[sid][key]['bills']+=1
  weekly[sid][key]['qty']+=bl.get(bid,{}).get('qty',0)
for sid in stores:
 for ds,v in foot[sid].items():
  d=date.fromisoformat(ds)
  if inper(d,RECENT):
   n=daily_bills[sid].get(ds,0)
   if v<0 or n>v or (n>0 and v==0):dq[sid].add(ds+': bills exceed footfall or invalid footfall')
   if not special(sid,d):normal[sid]['foot']+=v;normal[sid]['days']+=1
  if inper(d,PRIOR) and not special(sid,d) and v>0:
   normalp[sid]['foot']+=v;normalp[sid]['days']+=1
  if date(2026,10,18)<=d<=END and not special(sid,d):
   key='before' if d<date(2026,10,25) else 'after'
   weekly[sid][key]['foot']+=v
 for ds,n in daily_bills[sid].items():
  if n and ds not in foot[sid]:dq[sid].add(ds+': bills exist but footfall missing')
 s=out['stores'][sid]
 eligible={c for c,d in first_store[sid].items() if (END-d).days>=30}
 s['repeat30']=len(returned_store[sid]&eligible)/len(eligible) if eligible else None
 s['repeat_eligible']=len(eligible)
 s['understaffed_busy_days']=[ds for ds in s['understaffed_busy_days'] if not special(sid,date.fromisoformat(ds))]
 s['dq']=sorted(dq[sid]);s['normal_days']=int(normal[sid]['days']);s['excluded_event_days']=sum(special(sid,RECENT[0]+timedelta(days=i)) for i in range(28));s['missing_footfall_days']=28-len([ds for ds in foot[sid] if RECENT[0]<=date.fromisoformat(ds)<=END])
 s['normal_bills']=int(normal[sid]['bills']);s['normal_foot']=int(normal[sid]['foot'])
 s['normal_conv']=normal[sid]['bills']/normal[sid]['foot'] if normal[sid]['foot'] else None
 s['normal_ipb']=normal[sid]['qty']/normal[sid]['bills'] if normal[sid]['bills'] else None
 s['followup']={}
 for k,v in weekly[sid].items():
  s['followup'][k]={'conversion':v['bills']/v['foot'] if v['foot'] else None,'ipb':v['qty']/v['bills'] if v['bills'] else None,'bills':int(v['bills'])}
 for t in s.get('team',[]):
  el={c for c,d in first_sp[t['id']].items() if (END-d).days>=30}
  t['repeat_eligible']=len(el)
  t['repeat30']=len(returned_sp[t['id']]&el)/len(el) if el else None
  t['sherwani_bills']=int(spm[t['id']]['sher']);t['kurta_bills']=int(spm[t['id']]['kur'])
for sid,s in out['stores'].items():
 peers=[out['stores'][x] for x in city_peers[s['city']] if x!=sid and not out['stores'][x]['dq'] and out['stores'][x]['normal_days']>=7]
 for field in ['normal_conv','normal_ipb','repeat30']:
  vals=[x[field] for x in peers if x[field] is not None]
  s[field+'_peers']=statistics.median(vals) if vals else None
 s['peer_stores']=len(peers)
# city-wide footfall trend: a market signal, not one store's execution
for mgr in out['managers']:
 ch=[]
 for sid in mgr['stores']:
  s=out['stores'][sid]
  if s['dq'] or s['normal_days']<7 or normalp[sid]['days']<7:continue
  fp=normalp[sid]['foot']/normalp[sid]['days']
  if fp>0:ch.append((normal[sid]['foot']/normal[sid]['days'])/fp-1)
 if len(ch)>=2:
  mc=statistics.median(ch); down=sum(1 for x in ch if x<0)
  if mc<=-0.10 and down>len(ch)/2:
   mgr['market']={'stores_down':down,'stores_valid':len(ch),'median_chg':mc}
# No row-level customer or transaction information is exported.

print("window.AGG = "+json.dumps(out,separators=(",",":"))+";")
