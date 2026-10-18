import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import archive_explanations as explain
import archive_guides as guides


class ArchiveExplanationTests(unittest.TestCase):
    def test_programme_notes_cannot_be_published_as_an_argument_guide(self):
        work={'id':'test-notes','investor':'test','title':{'en':'Requested episode'},'sources':[{'url':'https://publisher.example/episode'}]}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);explain.write(root/'archive/catalog.json',{'works':[work]})
            with patch.object(explain,'obtain_material',return_value=('Topics only. '*200,'description',work['sources'][0]['url'])):
                result=explain.run(root,limit=1)
            self.assertEqual(result['generated'],0)
            self.assertFalse((root/'archive/explanations/test-notes.json').exists())
            self.assertIn('Programme topics',explain.read(root/'archive/explanations/index.json')['attempts']['test-notes']['reason'])

    def test_verified_written_version_precedes_a_podcast_description(self):
        url='https://podcasters.spotify.com/pod/show/author/episodes/requested'
        pdf='https://publisher.example/original.pdf'
        work={'sources':[{'url':url},{'url':pdf,'kind':'original_document'}]}
        with patch.object(explain.source,'fetch',return_value=(b'%PDF synthetic','application/pdf')) as fetch,patch.object(explain.source,'extract_text',return_value='Original author text. '*100):
            text,basis,origin=explain.obtain_material(work)
        fetch.assert_called_once_with(pdf)
        self.assertEqual((basis,origin),('original_document',url))
        self.assertEqual(work['_materialURL'],pdf)

    def test_complete_essay_with_audio_reading_keeps_its_original_text(self):
        work={'kind':'essay','sources':[{'url':'https://author.example/essay'}],'media':[{'kind':'audio','url':'https://author.example/audio.mp3'}]}
        with patch.object(explain.source,'obtain_text',return_value=('Original essay. '*100,'official_text',work['sources'][0]['url'])),patch.object(explain.source,'video_text') as asr:
            text,basis,origin=explain.obtain_material(work)
        self.assertEqual(basis,'official_text');asr.assert_not_called()

    def test_spotify_audio_redirect_is_decoded_before_full_recognition(self):
        import os
        wrapped='https://anchor.fm/s/123/podcast/play/123/https%3A%2F%2Fcdn.example%2Ffull.mp3'
        with patch.dict(os.environ,{'ARCHIVE_ALLOW_ASR':'1'}),patch.object(explain.source,'video_text',return_value=('Full recording','asr')) as asr:
            self.assertEqual(explain.episode_material({},'Programme notes','https://publisher.example/episode',wrapped)[1],'asr')
        self.assertEqual(asr.call_args.args[0]['media'][0]['url'],'https://cdn.example/full.mp3')

    def test_number_checks_preserve_decimal_suffixes_and_chinese_unit_conversions(self):
        chunks=[{'id':'s0','text':'The historical annual cost was HK$6.5bn. There are 0 1 2 3 4 5 synthetic sections.'}]
        note=self.note();note['sections'][0]['paragraphs'][0]={'zh':'文章估计成本为65亿港元。','en':'The article estimates HK$6.5 billion.'}
        self.assertIn('6.5',explain.NUMBER.findall('HK$6.5bn'))
        self.assertTrue(explain.validate(note,{},chunks,0))
        for zh,en in [('成本为650亿港元。','The cost was HK$65 billion.'),('成本为650万港元。','The cost was HK$6.5 million.')]:
            bad=copy.deepcopy(note);bad['sections'][0]['paragraphs'][0]={'zh':zh,'en':en}
            with self.assertRaisesRegex(ValueError,'numerical claim'):explain.validate(bad,{},chunks,0)
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
        self.assertEqual(explain.minimum({'id':'test'},{'test':650}),0)
        self.assertEqual(explain.minimum({'id':'new'},{}),0)

    def test_every_investor_has_a_distinct_detailed_collection_guide(self):
        data=explain.read(explain.ROOT/'archive/guides.json')['guides']
        people=explain.read(explain.ROOT/'investors.json')['investors']
        self.assertEqual(set(data),{p['id'] for p in people})
        for person in people:
            guide=data[person['id']]
            body=guide['lead']['zh']+' '.join(p['zh'] for s in guide['sections'] for p in s['paragraphs'])
            self.assertGreater(len(guide['sections']),1,person['id'])
            expected={w['id'] for w in explain.read(explain.ROOT/'archive/catalog.json')['works'] if w['investor']==person['id']}
            self.assertEqual({w['id'] for w in guide['works']},expected)
            baseline=explain.read(explain.ROOT/'archive/guide_expansion_baselines.json',{}).get(person['id'],0)
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

    def test_mixed_english_is_rejected_and_supported_author_attribution_is_allowed(self):
        chunks=[{'id':'s0','text':'Synthetic evidence includes sections 0 1 2 3 4 5.'}]
        mixed=self.note();mixed['sections'][0]['paragraphs'][0]['en']+=' 凝聚ing consensus.'
        with self.assertRaisesRegex(ValueError,'untranslated Chinese'):explain.validate(mixed,{},chunks,500)
        retelling=self.note();retelling['sections'][0]['paragraphs'][0]['zh']='帕伯莱指出，'+retelling['sections'][0]['paragraphs'][0]['zh']
        self.assertTrue(explain.validate(retelling,{'investor':'pabrai'},chunks,500))

    def test_podcast_uses_only_the_requested_episode_not_catalogue_navigation(self):
        work={'sources':[{'url':'https://valueinvestingwithlegends.libsyn.com/requested'}]}
        feed='<rss><channel><item><title>Unrelated guest</title><link>https://valueinvestingwithlegends.libsyn.com/other</link><description>Unrelated material</description></item><item><title>Requested episode</title><link>https://valueinvestingwithlegends.libsyn.com/requested</link><description>'+('Synthetic programme notes about business research. '*20)+'</description></item></channel></rss>'
        with patch.object(explain.source,'fetch',return_value=(feed.encode(),'application/xml')):
            text,basis,url=explain.obtain_material(work)
        self.assertNotIn('Unrelated guest',text)
        self.assertTrue(text.startswith('Requested episode'))
        self.assertEqual(basis,'description')

    def test_canonical_episode_notes_survive_a_broken_or_truncated_rss_feed(self):
        url='https://valueinvestingwithlegends.libsyn.com/requested'
        work={'investor':'abrams','title':{'en':'David Abrams - Requested episode'},'sources':[{'url':url}]}
        page=('<title>Value Investing with Legends: David Abrams - Requested episode</title><aside>Unrelated guest</aside><div class="libsyn-item" data-id="123"><p class="lead">David Abrams '+('Synthetic programme description for verification. '*30)+'</p></div>').encode()
        def get(target):return (page,'text/html') if target==url else (b'<rss><![CDATA[truncated','text/xml')
        with patch.object(explain.source,'fetch',side_effect=get):
            text,basis,origin=explain.obtain_material(work)
        self.assertEqual(basis,'description');self.assertEqual(origin,url)
        self.assertNotIn('Unrelated guest',text)
        with patch.object(explain.source,'fetch',return_value=(page.replace(b'Requested episode',b'Different episode'),'text/html')):
            with self.assertRaises(Exception):explain.obtain_material(work)


if __name__=='__main__':unittest.main()
