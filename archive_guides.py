"""Build detailed collection guides from reviewed profiles and real catalogues.

The reading commentary is editorial AI explanation, never an original transcript.
No inference about an unread individual work is made here.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
READING = {
 'lilu': ('李录的作品适合沿着经历与方法两条线阅读。较早的访谈说明他的成长和时代背景；序言、投资访谈与大学演讲，则帮助理解他如何把企业研究、能力圈和长期持有连接起来。阅读时不要只记住“长期”这个词：更值得追问的是，企业竞争优势能否持续、研究凭什么形成确信，以及在哪些问题上投资者必须承认自己不知道。宏观环境与单个企业也要分开理解，不能把演讲中的长期方法直接套成某一季度交易的原因。',
 'Read Li Lu along two threads: personal experience and investment method. Earlier interviews provide biographical context; forewords, investment interviews and university speeches illuminate business research, competence and long-term ownership. Go beyond remembering the word patience: ask why an advantage might endure, what supports conviction and what remains unknown. Keep the macro setting separate from an individual business, and do not turn a general investment principle into an explanation of a particular quarterly trade.'),
 'pabrai': ('帕伯莱的特色是把复杂的投资问题讲成容易记住的框架，但记住口号只是开始。“正面我赢，反面我也输不了多少”要求先研究下行情景：资产和现金流能提供什么保护、坏结果会不会造成永久损失，再考虑上行空间。Cloning 是寻找线索的方法，不能代替独立核查；清单也不是打勾仪式，而是防止自己重复犯错的工具。不同年份的访谈可以互相对照，关注一个想法经过实践后，哪些假设被修正，而不是只摘录最后的结论。',
 'Pabrai makes difficult investment questions memorable, but a slogan is only the beginning. Dhandho starts with the downside: what assets and cash flows protect capital, and which bad outcomes could cause permanent loss? Cloning supplies leads rather than replacing independent verification. A checklist guards against repeated mistakes instead of merely recording boxes ticked. Compare interviews across time to see which assumptions were revised through experience, rather than collecting conclusions without their conditions.'),
 'duan': ('段永平的访谈要结合经营者经验来读。“买股票就是买公司”意味着先理解产品、客户、商业模式和企业文化，再讨论价格是否合适。师生问答往往围绕具体问题展开，单独摘出一句回答容易丢掉前提；阅读时应把提问和回答一起保留在理解中。“不懂不做”不是降低研究要求，而是划清不能靠猜测跨越的边界。涉及股票、看涨期权、看跌期权的表达还要分别理解，不能把期权义务自动写成已经完成的现货买卖。',
 'Read Duan through his operating experience. Buying a stock as a business means understanding products, customers, economics and culture before discussing price. In student Q&A, a short answer often depends on the question that prompted it; keep both in view. Staying within competence sets a research boundary rather than lowering the standard of evidence. Distinguish shares, calls and puts, because a derivative obligation is not automatically a completed cash-equity trade.'),
 'tepper': ('泰珀的作品需要区分投资访谈与人生演讲。投资部分的关键通常是困境中的偿付能力、资产价值、政策和流动性：价格很低不等于损失很小，必须先理解企业能否活下来、资本结构中不同债权和股权承担什么风险。毕业演讲则提供个人经历和价值取向的背景，不应被当作一套交易规则。对照不同时点的采访时，应把当时的市场条件一起看，理解一个判断有哪些前提，以及环境变化后为什么需要重新检查。',
 'Separate Tepper’s investment interviews from personal speeches. In distressed investing, repayment capacity, asset value, policy and liquidity matter: a low price does not by itself limit loss. Understand survival and the different risks borne by debt and equity. Commencement remarks provide personal context rather than a trading rulebook. When comparing interviews, retain their market setting so that a conditional judgment is not mistaken for a timeless instruction.'),
 'webb': ('韦伯的公开研究把企业价值、股权关系和治理问题放在一起。阅读时可以先确定事实链：哪份公告支持哪项判断，谁控制公司，关联交易怎样影响小股东，管理层的利益是否与公众股东一致。“阳光是最好的消毒剂”在这里指向信息透明的价值，而不是一条估值公式。访谈能够解释他的研究取向，具体公司的结论仍应回到原始公告、财报和当时的股权结构。历史研究不能直接当成今天仍然持有某只股票的证明。',
 'Webb links business value, ownership networks and governance. Start with the evidence chain: which filing supports a claim, who controls the company, how related-party transactions affect minority investors and whether incentives align. Sunlight expresses the value of transparency rather than a valuation formula. Interviews explain his approach, while company-specific conclusions require contemporary filings and ownership records. Historical research does not establish a present holding.'),
 'buffett': ('巴菲特的资料应按年份连续阅读，而不是只收集名言。年会问答中的回答对应当时的问题、企业和资本配置环境；同一主题在不同年份的变化，往往比孤立的一句结论更有意义。阅读企业价值时，要分清会计利润、可分配现金、再投资需求和买入价格；阅读管理层时，则要看激励、诚信与资本使用方式。好的企业不自动等于任何价格都值得买，耐心持有也不等于停止检查生意。年会中其他发言人的观点应与巴菲特本人区分。',
 'Read Buffett chronologically rather than collecting quotations. Annual-meeting answers respond to particular questions, businesses and capital-allocation conditions. Changes in a topic across years can be more informative than an isolated conclusion. Distinguish accounting earnings, distributable cash, reinvestment needs and price, and examine management incentives and integrity. A good business is not attractive at every price, while patience does not remove the need to reassess its economics. Identify other meeting speakers separately.'),
 'akre': ('阿克瑞的“三条腿的凳子”适合拆开研究，再重新放在一起：生意本身是否优秀，管理层是否诚实且善于配置资本，企业是否还有能够获得较高回报的再投资机会。高回报率只是起点，如果赚到的钱无法继续高效投入，长期复利的空间就会收窄。阅读访谈时，可以关注他如何判断某条腿受损，以及为什么价格波动与生意质量的变化不是同一件事。这个框架的价值在于提供连续的检查顺序，不是把所有高 ROIC 公司直接选出来。',
 'Take Akre’s three-legged stool apart and then reconnect it: exceptional economics, trustworthy capital allocators and opportunities to reinvest at attractive returns. A high return alone is insufficient when future reinvestment opportunities disappear. Look for how interviews distinguish a damaged business leg from a moving market quotation. The framework supplies a sequence for continued appraisal, rather than automatically approving every company with a high historical return on capital.'),
 'greenberg': ('格林伯格的公开访谈适合围绕“为什么少数企业值得投入大量研究”来读。集中持仓提高了每个判断的重要性，因而需要同时理解竞争地位、客户关系、现金流与资本回报，不能用单一便宜指标代替企业研究。阅读时要把容易理解的商业模式与容易预测的经营结果分开：企业看起来简单，仍可能受到竞争、定价和管理层资本配置的影响。公开作品较少时，更应保留采访的上下文，不把其他作者对他的评价冒充本人的完整观点。',
 'Greenberg’s interviews are useful for asking why a small set of businesses deserves intensive research. Concentration raises the importance of each judgment, requiring competitive position, customer economics, cash generation and returns on capital to be considered together. An understandable model is not necessarily a predictable outcome. Competition, pricing and capital allocation still matter. When primary material is sparse, retain context and distinguish the investor’s own statements from commentary about him.'),
 'klarman': ('克拉曼的作品以保全资本和安全边际为阅读主线。首先理解他所说的风险：不是报价是否波动，而是哪些情景会使资本永久受损，以及投资者有没有能力熬过这些情景。保守估值、现金、流动性与仓位大小应一起讨论；看上去便宜的资产，如果需要额外投入或短期融资，也可能没有足够保护。阅读公开访谈时，要保留判断的条件，不能把逆向理解成与市场唱反调，也不能把耐心理解成忽略错误。',
 'Use capital preservation and margin of safety as the thread through Klarman’s work. Ask which outcomes could permanently impair capital and whether the investor can withstand them. Conservative appraisal, cash, liquidity and position size belong together. A seemingly cheap asset may offer little protection if it requires further funding. Preserve the conditions attached to a judgment: contrarian investing is not simply disagreement, and patience is not refusal to recognize a mistake.'),
 'ackman': ('阿克曼的作品可以把企业分析与推动价值兑现两条线分开看。前者解释商业模式、竞争优势、现金流和估值；后者涉及治理、资本配置、董事会与可能的变化路径。一个投资判断可能依赖经营结果，也可能依赖外部行动，二者需要不同的证据和时间尺度。访谈中的失败复盘尤其适合检验最初假设、执行难度和风险控制，但不能把事后成功总结成事前必然。不同阶段的投资方法也应按作品日期区分。',
 'Separate Ackman’s business analysis from his efforts to realize value. One concerns economics, competition, cash and valuation; the other concerns governance, capital allocation, boards and possible change. These require different evidence and time horizons. Discussions of setbacks help test assumptions, execution and risk control, but a successful outcome is not proof it was inevitable in advance. Keep the date and stage of his approach attached to each work.'),
 'abrams': ('艾布拉姆斯的公开资料较少，阅读重点应放在已经公开的研究过程，而不是替他补写投资故事。套利经历、通才式研究、基本面判断和确信度可以相互联系：广泛寻找机会并不意味着对每个行业都已有答案，投资者仍需知道哪些问题能核实、哪些变量难以估计。访谈中的退出、仓位与管理层讨论，应结合具体提问理解。节目说明只能帮助定位话题，不能替代完整录音，更不能据此推断没有公开的持仓动机。',
 'Abrams has relatively little public material, so focus on the process he has actually discussed rather than filling in a private investment story. Arbitrage experience, generalist research, fundamentals and conviction can be connected without assuming expertise in every industry. Understand which questions are verifiable and which variables resist estimation. Read discussions of exits, sizing and management with their questions. Programme descriptions locate topics but do not substitute for a full recording or reveal undisclosed motivations.'),
 'berkowitz': ('伯科威茨的作品要同时看现金和资产。土地、经营资产与账面价值提供了估值线索，但真正的问题是价值怎样变成股东能够获得的现金、需要等待多久，以及实现过程中会消耗多少资本。集中和逆向增加了对研究与耐心的要求，不能把账面折价本身当成结论。比较不同年份的访谈时，可以检查原先设想的资产处置、经营改善或资本配置是否按预期推进；企业有价值与投资回报能够及时兑现，是两个需要分别核实的问题。',
 'Read Berkowitz through both cash and assets. Land, operating assets and book value offer clues, but ask how value becomes distributable cash, how long realization may take and what capital it consumes. Concentration and contrarian positioning require evidence and patience, rather than treating a book discount as a conclusion. Compare interviews against the progress of asset sales, operating improvements and capital allocation. Business value and timely investment realization are distinct questions.'),
 'hawkins': ('霍金斯的“企业、管理者、价格”提供了清晰的阅读顺序。先像私人买家一样估算整个企业的经济价值，再判断管理层是否值得长期合作，最后检查报价是否留下足够折让。估值不应只看利润表，还需要理解资产、负债、现金创造能力和不同业务的价值。公开对谈也可帮助理解长期合伙文化与积极参与资本配置的关系。阅读时区分经营价值改善和市场价格回归，避免把任何一次上涨都当成最初估值已经被验证。',
 'Hawkins’s business, people and price provide a reading sequence. Appraise economic value as a private buyer, assess management as a long-term partner and then examine the price discount. Consider assets, liabilities, cash generation and distinct businesses alongside earnings. Conversations also illuminate partnership culture and engagement on capital allocation. Distinguish improvements in economic value from a market re-rating; a rising quote does not automatically validate the original appraisal.'),
 'vinall': ('维纳尔的资料适合把致投资人信和年度交流放在一起读。书面信件更容易看清当时如何解释企业、经营者和长期假设；问答则能补充这些判断受到怎样的质疑。关注管理层是否诚实、理性以及与股东利益一致，也要追问竞争优势能否积累、增长是否创造价值、企业如何重新投入现金。长期持有需要匹配企业和资本的时间尺度，并不意味着所有假设永远成立。不同年份的叙述应相互校验，避免把最新观点覆盖掉当时的原始条件。',
 'Read Vinall’s investor letters alongside annual gatherings. Letters record how he explained businesses, managers and long-term assumptions at the time; Q&A adds the challenges put to those judgments. Examine honest, rational, aligned management together with durable advantages, value-creating growth and reinvestment. Long-term ownership requires compatible business and capital horizons, not assumptions that can never change. Compare years without overwriting earlier conditions with today’s explanation.'),
}

def pair(zh, en): return {'zh': zh, 'en': en}

def build_guides(root=ROOT):
    root=Path(root)
    people=json.loads((root/'investors.json').read_text())['investors']
    catalog=json.loads((root/'archive/catalog.json').read_text())
    guides={}
    for p in people:
        profile=p['profile']; works=sorted([w for w in catalog['works'] if w['investor']==p['id']],key=lambda w:w.get('date') or '')
        principles=profile.get('principles',[])
        reading=READING.get(p['id'],(
            '阅读 '+p['name']+' 的公开作品时，可以先以已核对人物资料中的研究方法为线索，再沿作品日期比较判断的前提。具体篇目的内容仍以该篇原始材料为依据，不能把人物的一般理念直接当成每次交易的理由。',
            'Read '+p['nameEn']+' through the methods in the reviewed profile, then compare the conditions of judgments across dated works. Individual introductions must remain grounded in their own source; general principles do not establish trading motivations.'))
        sections=[{'heading':pair(*profile['signature']['title']), 'paragraphs':[pair(*profile['signature']['text']),pair(*reading)]},
                  {'heading':pair('把方法展开看','Understanding the method'), 'paragraphs':[pair(x['title'][0]+'：'+x['text'][0],x['title'][1]+': '+x['text'][1]) for x in principles]},
                  {'heading':pair('怎样安排阅读顺序','A reading sequence'), 'paragraphs':[pair(
                    '可以先读早期作品，再对照近期访谈或演讲，记录判断的前提、企业背景和后来发生的变化。先理解提问与回答的关系，再比较相同问题在不同年份的表达；不要把不同年份的材料拼接成一段从未说过的话。下面列出的篇目来自当前目录，目录仍可能遗漏公开作品。',
                    'Start with earlier works and compare later interviews or speeches, retaining assumptions, business context and subsequent changes. Read each answer with its question before comparing years. Do not splice separate works into a statement never made. The selections below come from the current catalogue, which may omit public material.')]}]
        extension_path=root/'archive/guide_extensions.json'
        extensions=json.loads(extension_path.read_text()) if extension_path.exists() else {}
        sections.extend(extensions.get(p['id'],[]))
        anchor_works=works[:1]+works[-2:] if len(works)>3 else works
        guides[p['id']]={'kind':'ai_collection_guide','investor':p['id'],'title':pair(p['name']+' · 作品阅读导读',p['nameEn']+' · Collection guide'),
                         'lead':pair(*profile['about'][0]),'sections':sections,'works':[{'id':w['id'],'title':w['title'],'date':w.get('date'),'publisher':w['publisher']} for w in anchor_works],
                         'sourceURLs':profile.get('sources',[]),'sourceHash':hashlib.sha256(json.dumps([profile,works,extensions.get(p['id'],[])],sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
                         'label':pair('AI 导读：依据已核对人物资料和目录编写，不是原文、逐句翻译或单篇全文的替代。','AI guide based on reviewed profiles and catalogue metadata; not an original text, literal translation or replacement for any individual work.')}
    path=root/'archive/guides.json';path.write_text(json.dumps({'version':1,'guides':guides},ensure_ascii=False,indent=2)+'\n')
    return guides

if __name__=='__main__':
    guides=build_guides();print('Detailed collection guides:',len(guides))
