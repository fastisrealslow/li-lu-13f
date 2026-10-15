import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import archive_explanations as explain
import archive_guides as guides


class ArchiveExplanationTests(unittest.TestCase):
    def note(self):
        # Synthetic material only; never published as an investor's words.
        words=['先核对企业经营结构','再区分现金流和账面利润','注意资本投入的长期影响','检查竞争条件与客户选择','分清价格波动和经济价值','保留当时判断的适用条件']
        return {'sourceSummary':{'zh':'测试资料讨论企业研究。','en':'The synthetic material discusses business research.'},
                'sections':[{'heading':{'zh':w,'en':'Independent analysis'},'paragraphs':[{'zh':w+'。'+('这个测试段落用于核查解释的长度和双语字段。'*10)+str(i),
                            'en':'A synthetic independent explanation for test section '+str(i)+'.'}],'evidenceIds':['s0']} for i,w in enumerate(words)]}

    def test_source_bound_validation_rejects_padding_missing_evidence_and_numbers(self):
        chunks=[{'id':'s0','text':'A synthetic source about business research, sections 0 1 2 3 4 5.'}]
        note=self.note()
        self.assertTrue(explain.validate(note,{},chunks,500))
        for change in ['number','chinese_number','evidence','translation','padding','length']:
            bad=copy.deepcopy(note)
            if change=='number':bad['sections'][0]['paragraphs'][0]['en']+=' Profit is 999%.'
            if change=='chinese_number':bad['sourceSummary']['zh']+='回报999%。'
            if change=='evidence':bad['sections'][0]['evidenceIds']=['invented']
            if change=='translation':bad['sections'][0]['paragraphs'][0]['en']=''
            if change=='padding':bad['sections'][1]['paragraphs']=bad['sections'][0]['paragraphs']
            if change=='length':bad['sections']=bad['sections'][:1]
            with self.subTest(change=change),self.assertRaises(ValueError):explain.validate(bad,{},chunks,500)

    def test_length_requirement_is_at_least_five_times_the_previous_edition(self):
        self.assertEqual(explain.minimum({'id':'test'},{'test':650}),3250)
        self.assertEqual(explain.minimum({'id':'new'},{}),1300)

    def test_every_investor_has_a_distinct_detailed_collection_guide(self):
        data=explain.read(explain.ROOT/'archive/guides.json')['guides']
        people=explain.read(explain.ROOT/'investors.json')['investors']
        self.assertEqual(set(data),{p['id'] for p in people})
        for person in people:
            guide=data[person['id']]
            body=guide['lead']['zh']+' '.join(p['zh'] for s in guide['sections'] for p in s['paragraphs'])
            self.assertGreater(explain.chinese_size(body),450,person['id'])
            self.assertTrue(guide['sourceURLs'])
            self.assertTrue(guide['works'])
        self.assertEqual(len({g['sections'][0]['paragraphs'][1]['zh'] for g in data.values()}),len(people))
        self.assertIn('三条腿',data['akre']['sections'][0]['heading']['zh'])
        self.assertIn('正面我赢',data['pabrai']['sections'][0]['heading']['zh'])

    def test_source_failure_keeps_previous_content_and_records_a_retry(self):
        work={'id':'lilu-test','investor':'lilu','title':{'zh':'测试','en':'Test'},'sources':[{'url':'https://publisher.example/test'}]}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            explain.write(root/'archive/catalog.json',{'works':[work]})
            explain.write(root/'archive/explanations/lilu-test.json',{'previous':'keep'})
            explain.write(root/'archive/explanations/index.json',{'entries':{'lilu-test':{'file':'archive/explanations/lilu-test.json','inputHash':'old'}},'attempts':{}})
            with patch.object(explain,'obtain_material',side_effect=TimeoutError):result=explain.run(root,limit=1)
            self.assertEqual(result['generated'],0)
            self.assertEqual(explain.read(root/'archive/explanations/lilu-test.json'),{'previous':'keep'})
            self.assertEqual(explain.read(root/'archive/explanations/index.json')['attempts']['lilu-test']['status'],'retry')

    def test_podcast_uses_only_the_requested_episode_not_catalogue_navigation(self):
        work={'sources':[{'url':'https://valueinvestingwithlegends.libsyn.com/requested'}]}
        feed='<rss><channel><item><title>Unrelated guest</title><link>https://valueinvestingwithlegends.libsyn.com/other</link><description>Unrelated material</description></item><item><title>Requested episode</title><link>https://valueinvestingwithlegends.libsyn.com/requested</link><description>'+('Synthetic programme notes about business research. '*20)+'</description></item></channel></rss>'
        with patch.object(explain.source,'fetch',return_value=(feed.encode(),'application/xml')):
            text,basis,url=explain.obtain_material(work)
        self.assertNotIn('Unrelated guest',text)
        self.assertTrue(text.startswith('Requested episode'))
        self.assertEqual(basis,'description')


if __name__=='__main__':unittest.main()
