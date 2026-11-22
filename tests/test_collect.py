import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from collect import normalize
from common import changes
class Collection(unittest.TestCase):
 def test_requires_matching_product_and_release_identity(self):
  with self.assertRaises(ValueError):normalize({'result':{'name':'php','releases':[]}},'php')
  with self.assertRaises(ValueError):normalize({'result':{'name':'wrong','releases':[{'name':'1'}]}},'php')
 def test_deadline_revision_is_a_real_change(self):
  a=[{'id':'php','releases':[{'name':'8','eolFrom':'2026-01-01'}]}];b=[{'id':'php','releases':[{'name':'8','eolFrom':'2027-01-01'}]}]
  self.assertEqual(changes(a,b)['changed'],1)
