"""Public application release RSS; no installed versions are ever included."""
import json
from datetime import datetime,timezone
from email.utils import format_datetime
from xml.etree.ElementTree import Element,SubElement,tostring

def write_feed(root,stage):
 data=json.loads((root/'data/github-releases.json').read_text());rss=Element('rss',version='2.0');c=SubElement(rss,'channel')
 for k,v in [('title','Rack Expiry · selected application releases'),('link','https://coolcode.ca/rackexpiry/#releases'),('description','Observed published non-prerelease releases from configured projects. Weekly checks; never a feed of installed versions.')]:SubElement(c,k).text=v
 for r in sorted(data['history'],key=lambda x:x['published_at'],reverse=True)[:200]:
  i=SubElement(c,'item');SubElement(i,'title').text=r['name']+' '+r['version'];SubElement(i,'link').text=r['url'];SubElement(i,'guid',isPermaLink='false').text='github-release:'+r['repository']+':'+str(r['release_id']);SubElement(i,'pubDate').text=format_datetime(datetime.fromisoformat(r['published_at'].replace('Z','+00:00')).astimezone(timezone.utc),usegmt=True);SubElement(i,'description').text='Published '+r['published_at']+'. First observed by this collector '+r['first_observed_at']+'. Check release notes and migration instructions before upgrading.'
 (stage/'releases.xml').write_bytes(tostring(rss,encoding='utf-8',xml_declaration=True))
