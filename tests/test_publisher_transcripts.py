import json
import unittest

import publisher_transcripts as reader
import speech_archive


def html(value):
    return ('<script>window.__s_data='+json.dumps(value)+';</script>').encode()


class PublisherTranscriptTests(unittest.TestCase):
    def test_all_full_sessions_are_combined_without_clips_other_years_or_duplicates(self):
        morning={'type':'cnbcvideo','subType':'full_length','vcpsId':1,'title':'Synthetic morning','url':'https://buffett.cnbc.com/video/2009/05/02/morning.html'}
        afternoon={**morning,'vcpsId':2,'title':'Synthetic afternoon','url':'https://buffett.cnbc.com/video/2009/05/02/afternoon.html'}
        clip={**morning,'subType':'clips','vcpsId':3}
        other={**morning,'vcpsId':4,'url':morning['url'].replace('2009','2010')}
        raw=html({'assets':[morning,afternoon,clip,other],'duplicate':[morning]});requested=[]
        def get(url):
            requested.append(url);asset=morning if url==morning['url'] else afternoon
            transcript={'chapters':[{'transcript':[{'in':0,'title':asset['title']+': '+('Synthetic original statements. '*50)}]}]}
            return html({'asset':{**asset,'transcript':transcript}}),'text/html'
        text,origins=reader.obtain(raw,'https://buffett.cnbc.com/2009-berkshire-hathaway-annual-meeting',get)
        self.assertEqual(requested,[morning['url'],afternoon['url']]);self.assertEqual(origins,requested)
        self.assertIn('Synthetic morning',text);self.assertIn('Synthetic afternoon',text)

    def test_missing_transcript_chapter_cannot_be_treated_as_a_complete_session(self):
        asset={'type':'cnbcvideo','subType':'full_length','vcpsId':1,'url':'https://buffett.cnbc.com/video/2009/05/02/morning.html'}
        with self.assertRaisesRegex(ValueError,'Incomplete meeting'):
            reader.obtain(html([asset]),'https://buffett.cnbc.com/2009-berkshire-hathaway-annual-meeting',lambda url:(html([{**asset,'transcript':{'chapters':[{'transcript':[]}]}}]),'text/html'))

    def test_interview_endpoint_is_bound_to_its_original_host_and_video_id(self):
        requested=[]
        for target in ['https://elsewhere.example/video/transcripts/18975','https://charlierose.com/video/transcripts/1']:
            raw=('<div class="transcript" data-url="'+target+'"></div>').encode()
            with self.assertRaisesRegex(ValueError,'matching publisher'):
                reader.obtain(raw,'https://charlierose.com/videos/18975',lambda url:requested.append(url))
        self.assertEqual(requested,[])

    def test_public_interview_transcript_preserves_speakers_and_excludes_related_cards(self):
        raw=b'<main>Unrelated recommendation<div class="transcript" data-url="/video/transcripts/18975"></div></main>'
        turns=''.join(f'<dt>00:0{i}</dt><dd><a>Speaker {i}:</a><span data-time="{i*1000}">'+('Synthetic answer for testing public transcript extraction. '*7)+'</span></dd>' for i in range(5))
        get=lambda url:(('<dl>'+turns+'</dl>').encode(),'text/html')
        text,origins=reader.obtain(raw,'https://charlierose.com/videos/18975',get)
        self.assertIn('[00:04] Speaker 4:',text);self.assertNotIn('recommendation',text)
        self.assertEqual(origins,['https://charlierose.com/video/transcripts/18975'])
        work={'sources':[{'url':'https://charlierose.com/videos/18975'}]}
        material,basis,url=speech_archive.obtain_text(work,get=lambda url:(raw,'text/html') if '/videos/' in url else get(url))
        self.assertEqual(material,text);self.assertEqual(basis,'official_transcript')


if __name__=='__main__':unittest.main()
