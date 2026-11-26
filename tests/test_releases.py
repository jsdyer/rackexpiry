import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from collect_releases import normalize,collect,projects,NoRedirect
from release_feed import write_feed
P={'id':'new-app','name':'New & useful','repository':'org/new-app'}
RAW={'id':42,'tag_name':'v1.2.3','published_at':'2026-11-01T00:00:00Z','draft':False,'prerelease':False,'html_url':'https://github.com/org/new-app/releases/tag/v1.2.3'}
class Releases(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);(self.root/'config').mkdir();(self.root/'data').mkdir();(self.root/'config/releases.json').write_text(json.dumps({'projects':[P]}))
 def test_expanded_config_and_source_validation(self):
  self.assertEqual(projects(self.root),[P]);self.assertEqual(normalize(RAW,P)['version'],'v1.2.3')
  for fields in [{'draft':True},{'prerelease':True},{'html_url':'javascript:alert(1)'},{'published_at':None}]:
   with self.assertRaises(ValueError):normalize({**RAW,**fields},P)
 def test_refresh_preserves_first_observation_and_release_history(self):
  with patch('collect_releases.request',return_value=RAW),patch('collect_releases.now',return_value='2026-11-25T00:00:00Z'):first=collect(self.root)
  with patch('collect_releases.request',return_value=RAW),patch('collect_releases.now',return_value='2026-11-26T00:00:00Z'):second=collect(self.root)
  self.assertEqual(first['history'],second['history']);self.assertNotEqual(first['checked_at'],second['checked_at'])
  changed={**RAW,'id':43,'tag_name':'v1.2.4'}
  with patch('collect_releases.request',return_value=changed):third=collect(self.root)
  self.assertEqual(len(third['history']),2)
  before=(self.root/'data/github-releases.json').read_bytes()
  with patch('collect_releases.request',side_effect=RuntimeError('failed')):
   with self.assertRaises(RuntimeError):collect(self.root)
  self.assertEqual(before,(self.root/'data/github-releases.json').read_bytes())
 def test_feed_uses_publisher_date_stable_id_and_escapes_names(self):
  with patch('collect_releases.request',return_value=RAW):collect(self.root)
  write_feed(self.root,self.root);item=ET.parse(self.root/'releases.xml').find('./channel/item');self.assertEqual(item.findtext('title'),'New & useful v1.2.3');self.assertEqual(item.findtext('guid'),'github-release:org/new-app:42');self.assertIn('01 Nov 2026',item.findtext('pubDate'))
 def test_credentials_cannot_follow_a_redirect(self):self.assertIsNone(NoRedirect().redirect_request(None,None,302,'Redirect',{},'https://elsewhere.example/'))
