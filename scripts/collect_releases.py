"""Collect selected public GitHub release metadata, never installed versions."""
import json,os,re,urllib.request
from pathlib import Path
from datetime import datetime
from common import ROOT,now

def projects(root=ROOT):
 rows=json.loads((root/'config/releases.json').read_text())['projects'];ids=set();repos=set()
 if not isinstance(rows,list) or not 1<=len(rows)<=100:raise ValueError('Configure 1–100 public projects')
 for r in rows:
  if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',r.get('id','')) or not isinstance(r.get('name'),str) or not 1<=len(r['name'])<=160 or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',r.get('repository','')):raise ValueError('Invalid project configuration')
  if r['id'] in ids or r['repository'].lower() in repos:raise ValueError('Duplicate project')
  ids.add(r['id']);repos.add(r['repository'].lower())
 return rows

def normalize(raw,project):
 repo=project['repository'];tag=raw.get('tag_name');stamp=raw.get('published_at');url=raw.get('html_url','')
 if raw.get('draft') is not False or raw.get('prerelease') is not False or not isinstance(tag,str) or not 1<=len(tag)<=160:raise ValueError('Expected a published, non-prerelease tag')
 if not isinstance(raw.get('id'),int) or raw['id']<=0 or not isinstance(stamp,str):raise ValueError('Missing release identity/date')
 datetime.fromisoformat(stamp.replace('Z','+00:00'))
 if not url.startswith('https://github.com/'+repo+'/releases/tag/'):raise ValueError('Unexpected release source URL')
 return {**project,'version':tag,'published_at':stamp,'release_id':raw['id'],'url':url,'source':'https://api.github.com/repos/'+repo+'/releases/latest'}

class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None

def request(url,headers):
 req=urllib.request.Request(url,headers={'User-Agent':'CoolCode Rack Expiry (+https://coolcode.ca/rackexpiry/)',**headers})
 # A fixed-host request with redirects disabled keeps the optional token at GitHub.
 try:
  with urllib.request.build_opener(NoRedirect).open(req,timeout=30) as response:raw=response.read(2_000_001)
 except OSError:raise RuntimeError('GitHub release request failed; retained catalogue unchanged') from None
 if len(raw)>2_000_000:raise ValueError('Release metadata exceeds size limit')
 return json.loads(raw)

def collect(root=ROOT):
 stamp=now();rows=[];headers={'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}
 # This token is supplied by GitHub Actions; only the fixed api.github.com host receives it.
 if os.environ.get('GITHUB_TOKEN'):headers['Authorization']='Bearer '+os.environ['GITHUB_TOKEN']
 for project in projects(root):
  url='https://api.github.com/repos/'+project['repository']+'/releases/latest'
  rows.append(normalize(request(url,headers),project));print('Checked public release: '+project['name'])
 target=root/'data/github-releases.json';previous=json.loads(target.read_text()) if target.exists() else {};history=previous.get('history',[]);seen={(r['repository'],r['release_id']) for r in history}
 for row in rows:
  if (row['repository'],row['release_id']) not in seen:history.append({**row,'first_observed_at':stamp})
 payload={'schema':1,'checked_at':stamp,'records':rows,'history':history,'note':'GitHub latest published non-prerelease releases for configured projects; may differ from distribution packages. First observation is not release time.'}
 temporary=target.with_suffix('.tmp');temporary.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');temporary.replace(target)
 return payload
if __name__=='__main__':collect()
