import unittest
from holdings_diff import consolidate_holdings
from reporting_scope import parse_cover
import speech_archive as archive


class ReportingScopeTests(unittest.TestCase):
    def test_numbered_managers_are_resolved_from_cover_not_guessed_from_ticker(self):
        cover=b'<root><otherManager2><sequenceNumber>6</sequenceNumber><otherManager><cik>123</cik><name>Separate vehicle</name></otherManager></otherManager2></root>'
        result=parse_cover(cover,'https://www.sec.gov/Archives/cover.xml','2026 Q2')
        self.assertEqual(result['managers']['6'],{'name':'Separate vehicle','cik':'123'})

    def test_one_row_with_multiple_managers_is_not_counted_multiple_times(self):
        base={'ticker':'TEST','cusip':'1','shares':10,'value':100,'managerAllocations':[{'managerIds':['1','2'],'shares':10,'value':100}]}
        other={**base,'shares':20,'value':200,'managerAllocations':[{'managerIds':['1','6'],'shares':20,'value':200}]}
        row=consolidate_holdings([base,other])[0]
        self.assertEqual((row['shares'],row['value']),(30,300))
        self.assertEqual(len(row['managerAllocations']),2)
        self.assertEqual(len(base['managerAllocations']),1)

    def test_buffett_letters_do_not_attribute_abels_annual_letter_to_buffett(self):
        source={'adapter':'buffett_letters','url':'https://www.berkshirehathaway.com/letters/letters.html','publisher':'Berkshire Hathaway'}
        html=b'<a href="2023ltr.pdf">2023</a><a href="2025ltr.pdf">2025</a><a href="other.html">Company news</a>'
        works=archive.link_catalog(source,lambda url:(html,'text/html'))
        self.assertEqual([w['date'] for w in works],['2023'])
        self.assertEqual(works[0]['kind'],'essay')

    def test_feed_author_filter_does_not_assign_another_authors_work(self):
        source={'url':'https://publisher.example/feed','investor':'webb','publisher':'Publisher','authorPattern':'^Webb-site.com$'}
        raw=b'<rss xmlns:dc="http://purl.org/dc/elements/1.1/"><channel><item><title>Another author</title><link>https://publisher.example/other</link><dc:creator>Other guest</dc:creator></item><item><title>Verified essay</title><link>https://publisher.example/own</link><dc:creator>Webb-site.com</dc:creator></item></channel></rss>'
        self.assertEqual([w['title']['en'] for w in archive.rss_catalog(source,lambda u:(raw,'text/xml'))],['Verified essay'])
