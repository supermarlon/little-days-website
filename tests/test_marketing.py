import datetime as dt, importlib.util, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('loop',Path(__file__).resolve().parents[1]/'scripts/marketing/loop.py');loop=importlib.util.module_from_spec(spec);spec.loader.exec_module(loop)
NOW=dt.datetime(2026,10,10,tzinfo=dt.timezone.utc)
class MeasurementTests(unittest.TestCase):
 def test_no_credentials_never_turns_into_zero(self):
  with patch.dict(loop.os.environ,{},clear=True),tempfile.TemporaryDirectory() as temp:
   obs=loop.collect(NOW,Path(temp)/'absent.json')
   self.assertEqual(obs['sources']['analytics']['status'],'missing_credentials')
   self.assertIsNone(obs['sources']['analytics']['metrics'])
   self.assertEqual(loop.plan(obs,{'experiments':[]},NOW)['next_action'],'establish_baseline')
 def test_api_answer_cannot_be_consumer_ranking(self):
  with self.assertRaises(ValueError):loop.validate_geo({'samples':[{'surface':'model_api'}]},NOW)
 def test_stale_geo_does_not_count_as_current(self):
  sample={'date':'2026-01-01','engine':'ChatGPT','prompt_id':'brand','surface':'consumer_search','mentioned':True,'cited':True}
  self.assertEqual(loop.validate_geo({'samples':[sample]},NOW)['status'],'stale')
 def test_no_winner_from_sparse_data(self):
  e={'id':'e','status':'running','started_at':'2026-08-01','baseline':{'ld_pageview':20,'ld_contact':2}}
  obs={'sources':{'analytics':{'status':'connected','metrics':{'ld_pageview':80,'ld_contact':30}}}}
  self.assertEqual(loop.evaluate(e,obs,NOW)['decision'],'insufficient_sample')
 def test_window_is_respected(self):
  e={'id':'e','status':'running','started_at':'2026-10-01','baseline':{'ld_pageview':1000,'ld_contact':30}}
  self.assertEqual(loop.evaluate(e,{},NOW)['decision'],'observe')
 def test_secrets_are_not_in_errors(self):
  self.assertEqual(loop.safe_error(RuntimeError('token secret123')),'provider_unavailable')
 def test_gsc_uses_aggregate_and_lag(self):
  with patch.dict(loop.os.environ,{'GSC_ACCESS_TOKEN':'test'},clear=True),patch.object(loop,'request_json',return_value={'rows':[]}) as request:
   data=loop.gsc(NOW); body=request.call_args.args[1]
   self.assertEqual(body['dimensions'],[]);self.assertEqual(body['endDate'],'2026-10-07');self.assertIsNone(data['metrics'])
 def test_posthog_only_returns_scoped_counts(self):
  with patch.dict(loop.os.environ,{'POSTHOG_READ_KEY':'test'},clear=True),patch.object(loop,'request_json',return_value={'results':[['ld_pageview',12],['ld_contact',2]]}) as request:
   data=loop.posthog(NOW)
   self.assertEqual(data['metrics']['ld_contact'],2)
   self.assertIn("properties.site = 'little-days-marketing'",request.call_args.args[1]['query']['query'])
 def test_daily_rerun_does_not_duplicate_history(self):
  import json
  with patch.dict(loop.os.environ,{},clear=True),tempfile.TemporaryDirectory() as temp:
   p=Path(temp);loop.run(p,p/'geo.json',NOW);loop.run(p,p/'geo.json',NOW)
   self.assertEqual(len(json.loads((p/'history.json').read_text())),1)
if __name__=='__main__':unittest.main()
