"""Daily discovery and rotating source rechecks, independent of generation."""
import datetime as dt
import hashlib
from pathlib import Path
import archive_explanations as e
import speech_archive as source


def discover(root=e.ROOT,now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    root=Path(root);catalog=e.read(root/'archive/catalog.json',{})
    # Keep check state private so an unchanged discovery cannot force deployment.
    marker=root/'.archive-work/discovery.json'
    state=e.read(marker,{})
    if state.get('day')==now.date().isoformat():return
    source.discover(root)
    catalog=e.read(root/'archive/catalog.json')
    index=e.read(root/'archive/explanations/index.json',{'entries':{}})
    checked=state.get('checked',{})
    changed=False
    attempts=0
    for work in sorted(catalog['works'],key=lambda w:checked.get(w['id'],'')):
        entry=index['entries'].get(work['id'],{})
        if entry.get('reviewStatus')!='verified':continue
        # Spread completed works over the week and cap daily network work.
        if int(hashlib.sha256(work['id'].encode()).hexdigest(),16)%7!=now.weekday():continue
        if checked.get(work['id'])==now.date().isoformat():continue
        if attempts>=3:break
        attempts+=1
        try:
            text,basis,url=e.obtain_material(work)
            if basis=='description' or len(source.source_chunks(text))<2:continue
            digest=hashlib.sha256(text.encode()).hexdigest()
            if entry.get('sourceDigest') and digest!=entry['sourceDigest']:
                work['sourceRevision']=digest;changed=True
            e.write(root/'.archive-work/partials'/('material-'+work['id']+'.json'),
                    {'inputHash':e.input_hash(work),'text':text,'basis':basis,'url':url})
            checked[work['id']]=now.date().isoformat()
        except Exception as exc:
            print('Source recheck retained:',work['id'],type(exc).__name__,flush=True)
    if changed:
        catalog['updatedAt']=now.isoformat(timespec='seconds');e.write(root/'archive/catalog.json',catalog)
    e.write(marker,{'day':now.date().isoformat(),'checked':checked})


if __name__=='__main__':
    import archive_budget as budget
    with budget.limit(600):discover()
