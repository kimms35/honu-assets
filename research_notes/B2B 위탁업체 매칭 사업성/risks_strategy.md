# B2B 위탁업체 매칭 마켓플레이스 (한국): 핵심 리스크와 진입 전략

> 방법 메모: 2026-11-27 기준 조사. 이 세션에서는 a16z.com, nfx.com, tech42.co.kr, hokodo.co 원문 페이지를 열 수 없었다(네트워크 허용 목록 밖). 그래서 이 사이트들에서 나온 내용은 검색엔진 요약/발췌를 근거로 한다. Lenny Rachitsky의 수수료율 연구와 마켓플레이스 시리즈는 유료 구독 전용이라 요약만 확인했다. 아래 인용은 모두 출처 원문 그대로가 아니라 해당 출처 기준의 진술이며, 인용 표시된 사이트를 직접 확인하는 것이 좋다.

## 1. 탈중개(누수, Disintermediation): 근거와 완화책

### Takeaway
B2B 서비스 마켓플레이스에서 누수는 실재하고, 측정이 어렵고, 반복 거래가 많은 1:1 관계일수록 심해진다. 수수료를 도입하면 누수가 측정 가능할 만큼 늘어난다. 효과가 입증된 대응은 금지/감시보다 플랫폼 안에서 거래하는 것을 더 가치 있게 만드는 쪽이다. 구체적으로는 관리형 서비스, 에스크로/결제 보호, 외상거래·금융, 보험·보증, 업무 SaaS가 있다.

### Cited Findings
- 근거(학술): Lalamove 대상 Northwestern 연구는 수수료 도입이 누수를 거의 4%p 늘렸다고 보고했다. 이는 탐지된 탈중개 거래가 두 배가 된 수준이다. 저자들이 제안한 완화책은 타겟 쿠폰, 모니터링 기술, 매칭 정책이다 — [PKU/PHBS seminar abstract, "Platform Leakage"](https://english.phbs.pku.edu.cn/info/3882/48882.htm)
- 누수 대응으로 마켓플레이스+리셀러 하이브리드(플랫폼이 자기 장부로 사서 되파는 구조) 모델을 다룬 2026 BU Platform Strategy 논문이 있다 — [BU Questrom Platform Strategy 2026 paper](https://questromworld.bu.edu/platformstrategy/wp-content/uploads/sites/49/2026/07/1085-Danhou.pdf); 판매자가 수수료를 우회하는 경우의 가격 처방은 [INFORMS Operations Research (2025)](https://pubsonline.informs.org/doi/fpi/10.1287/opre.2025.2046)가 다룬다
- 누수는 "실질적으로 정확한 측정이 거의 불가능"하다. 고위험 유형은 반복 주문이 잦은 공급(supply) 마켓플레이스다. Hokodo는 B2B 외상거래(net terms)/BNPL을 플랫폼에 머물게 하는 동기로 내세운다(벤더 출처이니 감안할 것) — [Hokodo](https://www.hokodo.co/resources/how-to-prevent-disintermediation-on-your-b2b-marketplace)
- a16z 마켓플레이스 용어집: 사용자가 우회하는 이유는 (1) 가격 민감도(수수료 회피), (2) 편의성(독점적 반복 거래에서는 오프라인 전환이 편함), (3) 필요성이다. 관리형 모델은 "거래 성사 과정 자체에 더 많은 가치를 줘서" 탈중개를 막는다. 관리형은 대체로 수수료율이 높지만 운영 부담이 크고 수익성을 내기 어렵다 — [a16z Marketplace Glossary](https://a16z.com/the-marketplace-glossary/)
- 소비자가 한 공급자와 반복해서 매칭되면 탈중개 위험이 커진다. 정신건강 분야에서는 청구·보험 처리를 플랫폼이 맡아서 양쪽 모두 플랫폼을 빼지 않는다(보험 적용을 잃기 때문) — [a16z, Healthcare marketplaces](https://a16z.com/healthcare-marketplaces-where-art-thou/)
- 저빈도 마켓플레이스 창업자가 마주하는 다른 종류의 위험은 "탈중개와 경쟁"이며, 고객을 "다시 획득"하는 강력한 성장 루프가 필요하다 — [a16z, Four paths to marketplace success / Marketplace 100](https://a16z.com/four-paths-to-marketplace-success/)
- 반대 관점: B2B는 주문 금액이 크고 업무 흐름이 복잡해서 온라인으로 거래를 잡아두기는 어렵다. 대신 이 특성이 탈중개 위험을 낮추고 SaaS처럼 끈끈한 사용자 기반을 만들어야 한다는 주장이 있다 — [Point Nine, A Primer on B2B Marketplaces](https://medium.com/point-nine-news/a-primer-on-b2b-marketplaces-challenges-and-opportunities-694a067cec91)
- 마켓플레이스 보험의 예: 결제가 플랫폼을 거칠 때만 손실을 보상한다 — [Sharetribe](https://www.sharetribe.com/academy/how-to-discourage-people-from-going-around-your-payment-system/)
- 사후 대응 수단: ML/NLP로 메시지를 감시해 누수 신호를 잡는다 — [LatentView](https://www.latentview.com/blog/how-to-prevent-disintermediation-at-the-marketplace/); 판매자가 구매자 신원을 볼 수 있다면 수수료는 낮게 잡아야 한다 — [VentureBeat](https://venturebeat.com/ai/how-to-protect-yourself-as-middleman-in-a-marketplace)
- 한국 사례(캐파/에이팀벤처스): 캐파는 처음에 직접 게이트키핑과 제조 대행을 하는 관리형으로 시작했다. 확장성 한계 때문에 개방형 플랫폼으로 바꿨다 — [Tech42 interview with 고산 대표](https://www.tech42.co.kr/?p=15953). 이후 에스크로 방식의 "캐파결제"를 내놨는데, 구매자가 완성품을 검수하고 구매를 확정해야 제조사에 대금이 지급된다 — [Tech42, 캐파결제](https://www.tech42.co.kr/?p=68611). 사용자 간 연락용 "안심번호"도 도입했다(연락처를 가리는 장치) — [Tech42, 안심번호](https://www.tech42.co.kr/?p=75435). 대규모 업데이트 때는 "캐파결제 수수료 0원" 이벤트로 결제 사용을 유도했다 — [Tech42 update](https://www.tech42.co.kr/?p=72198)
- 한국 사례(번개장터): 번개페이 사용을 모든 거래에 의무화하고 3.5% 수수료를 판매자 부담으로 바꿨다. 판매자 반발이 컸다고 보도됐다(C2C 사례지만 결제 강제의 실행 리스크를 보여준다) — [요즘IT (Wishket)](https://yozm.wishket.com/magazine/detail/2710/)

### Inferences
- 위탁 제조/서비스에서는 첫 매칭 이후 구매자-공급자가 짝을 이루는 경우가 많다. 두 번째 주문부터는 순수 거래 수수료가 누수될 가능성이 높다고 봐야 한다. 매칭 후에도 계속 가치를 주는 것이 있을 때만 수수료를 지킬 수 있다. 에스크로/검수, 외상거래, 품질 보증/재작업 보장, 세금계산서·정산 자동화, 발주·납기 추적 SaaS가 그런 예다.
- 한국 맥락의 함의: 캐파의 흐름(관리형 → 개방형 + 에스크로 + 연락처 마스킹)은 국내 제조 RFQ 마켓에서 실제로 쓰인 방어 수단 묶음이다. 결제 보호를 무료/저가로 제공해 유도하는 방식은 번개장터식 강제보다 반발이 적다.
- 측정이 어려우므로 MVP 단계에서 대리 지표를 설계해야 한다. 예를 들어 매칭된 구매자-공급자 쌍의 2회차 RFQ가 플랫폼에서 나오는 비율을 본다.

### Gaps
- 한국 B2B 마켓에서 누수율을 정량화한 자료(예: 캐파 재주문 중 플랫폼 경유 비율)는 찾지 못했다.
- 캐파결제의 실제 수수료율과 현재(2026) 수익 구조는 확인되지 않았다.
- a16z/NFX 원문은 접속이 막혀 직접 읽지 못했다. NFX "24 Ways B2B Marketplaces"(https://nfx.com/post/24-ways-b2b-marketplace)의 세부 메커닉은 미확인이다.

## 2. 닭과 달걀: 산업 분야에서 공급 먼저 확보하는 전술

### Takeaway
산업형 RFQ 마켓은 대체로 공급 측을 먼저 잡는다. 수단은 공공 등록 데이터, 직접 영업/관리형 운영, 공급자용 SaaS 도구다. 공공 데이터(팩토리온 전국등록공장현황)는 공급자 리스트를 공짜로 만들 수 있게 해준다. 하지만 가입 여부는 실제 수요(RFQ)를 보여줄 수 있느냐에 달려 있다. 국내 사례(캐파)에서는 관리형으로 수요를 먼저 증명한 뒤 공급이 입소문으로 늘었다.

### Cited Findings
- 한국산업단지공단 "전국등록공장현황"(팩토리온 기반): 공장 기본정보, 업종명·업종코드·생산품, 면적 등이 포함된 대용량 파일로 공공데이터포털에서 받을 수 있다 — [data.go.kr 15106170](https://www.data.go.kr/data/15106170/fileData.do). 산업단지별 공장 데이터(업체 수, 고용인원, 2006.6~2025.8 시점)도 있다 — [data.go.kr](https://www.data.go.kr/data/15127209/fileData.do)
- 한계: 지자체 데이터 설명에 따르면 공장 등록 의무는 건축면적 500㎡ 이상에만 적용된다. 그래서 소규모 사업장(소형 CNC·인쇄·포장 공방 등)은 빠질 수 있다 — [data.go.kr 지자체 공장등록 데이터](https://www.data.go.kr/data/15119039/fileData.do)
- 캐파: 파트너사가 입소문으로 10 → 100 → 500 → 2,000곳으로 늘었다. 고객이 도면과 견적요청서를 올리면 약 2,000개 제조사에 알림이 가고, 고객은 1차 견적을 비교해 업체를 고른다 — [Tech42 interview](https://www.tech42.co.kr/?p=15953)
- "Come for the tool, stay for the network"는 a16z Chris Dixon이 만든 말이다. SaaS-enabled marketplace는 SaaS 도구로 한쪽을 먼저 확보하고, 규모가 생기면 다른 쪽을 붙이는 전략이다. Point Nine은 반대로 마켓플레이스가 어느 정도 유동성을 확보한 뒤에 SaaS를 붙이는 편이 많은 경우 더 효과적이라고 주장한다 — [Point Nine, Come for the Network, Stay for the Tool](https://writing.pointnine.com/p/come-for-the-network-stay-for-the); [Sifted, B2B networks](https://sifted.eu/articles/b2b-networks)
- NFX James Currier: 마켓 네트워크는 전문가가 핵심 업무를 처리하게 해주는 SaaS 도구로 시작하는 경우가 많다. 또 B2B에서는 네트워크 효과보다 끈끈함(stickiness)이 먼저다 — [Bowery Capital, Investing in B2B marketplaces (Currier)](https://bowerycap.com/blog/insights/investing-in-b2b-marketplaces-james-currier-nfx-guild/); [NFX, 10 years about market networks](https://www.nfx.com/post/10-years-about-market-networks)
- Sarah Tavel의 Hierarchy of Marketplaces: 규모를 쫓기 전에 작고 제한된 시장에서 "minimum viable happiness"를 먼저 풀어야 한다. "GMV는 허영 지표이고 Happy GMV가 중요하다" — [Sarah Tavel, Hierarchy of Marketplaces](https://sarahtavel.medium.com/the-hierarchy-of-marketplaces-introduction-and-level-1-983995aa218e); [playbooks.com summary](https://playbooks.com/skills/wdavidturner/product-skills/hierarchy-of-marketplaces)
- Lenny Rachitsky의 마켓플레이스 킥스타트 시리즈(2019), "Why marketplaces fail", "How marketplaces win"은 유료 구독 전용이라 제목만 확인했다 — [Lenny's Newsletter marketplaces tag](https://www.lennysnewsletter.com/t/marketplaces)
- 공급 측 B2B 역방향 사례: "일깜"은 청소·인테리어·폐기물 업체들이 남는 일감을 서로 공유하는 B2B 앱이다(공급자끼리의 거래를 쐐기로 쓴 사례) — [App Store 일깜](https://apps.apple.com/kr/app/%EC%9D%BC%EA%B9%9C-%EC%B2%AD%EC%86%8C-%ED%94%8C%EB%9E%AB%ED%8F%BC/id6743198587)

### Inferences
- 실행 순서 제안: (1) 팩토리온 CSV를 업종코드로 걸러 목표 업종 공급자 DB를 만든다(예: 목재 포장, 골판지, 금속 가공). 지역은 1~2개 산단으로 좁힌다. (2) 실제 RFQ를 들고 전화/방문 영업을 한다. "견적 요청이 왔으니 견적 내시겠냐"가 가장 강한 가입 동기다. (3) 무료 검증 배지와 견적서·발주 관리 도구로 붙잡아 둔다.
- 500㎡ 미만 소규모 업체는 팩토리온에서 빠지므로 사업자등록 데이터, 네이버 플레이스·지도, 협회 회원 명부로 보완해야 한다.
- 수요 측은 초기에 관리형(컨시어지)으로 직접 처리하는 것이 국내외 사례 모두와 맞는다(캐파 초기, a16z 관리형 논리).

### Gaps
- 팩토리온 데이터의 최신 집계 기준일과 업종별 공장 수(예: 목재 포장재 제조 업종 수)는 직접 집계하지 못했다.
- 국세청 사업자 데이터를 업종 단위로 대량 활용할 수 있는지와 그 법적 제약(개인정보, 영업 목적 활용)은 조사하지 못했다.
- 국내 산업 마켓에서 공급자 확보 비용(CAC)을 다룬 자료는 없었다.

## 3. 파편화: 수평형 B2B 디렉터리 대 수직형

### Takeaway
수평형 B2B 디렉터리/익스체인지는 탐색 이상의 가치를 주지 못해서 일회성 거래와 높은 이탈에 시달린다. 업종마다 구매자가 따로 움직이기 때문에 카테고리를 넓힐 때마다 양쪽 사용자를 새로 모아야 한다. 이기는 패턴은 수직형 쐐기에서 출발해 발주·결제·업무 흐름까지 소유하는 "조달 운영체제"로 넓히는 것이다.

### Cited Findings
- 범용 서비스 플랫폼은 매칭 외에 주는 가치가 적다. 대부분의 서비스 업종에서 거래가 "가치가 제한적인 일회성 거래"라 장기 협업을 만들지 못하고 양쪽 이탈이 크다. 이 기사는 "vertical market networks"를 다음 흐름으로 제시한다 — [TechCrunch 2019, vertical market networks](https://techcrunch.com/2019/06/24/the-next-service-marketplace-wave-vertical-market-networks)
- 기업 구매자는 업종별 특성에 따라 사일로로 움직인다. 그래서 카테고리 확장이 어렵다(새 업종마다 구매자·판매자를 새로 온보딩해야 함) — [TechCrunch](https://techcrunch.com/?p=1982888)
- B2B 구매자는 보통 2~3개 플랫폼만 쓴다. 그래서 업종마다 소수의 전문 마켓만 살아남는다 — [BCG 2024, How B2B marketplaces are rewriting rules of trade](https://bcg.com/publications/2024/how-b2b-marketplaces-are-rewriting-rules-of-trade)
- 파편화된 B2B 시장에서는 주문·결제·업무를 잡는 소프트웨어가 진짜 제품이다. 승자는 "공급자 검색엔진"보다 "조달 운영체제"에 가까워진다 — [Sacra, Vertical SaaS operating systems win](https://sacra.com/chat/h/3071fbbd-9213-4d9f-9707-e5d9113c9c37/)
- 시장의 파편화와 비조직화는 업종이 디지털 전환에 무르익었다는 신호다 — [Alter, Verticalization of B2B e-commerce marketplaces](https://medium.com/alterglobal/verticalization-of-b2b-e-commerce-marketplaces-32ccc5b38dfd)
- 2000년대 B2B 익스체인지 붕괴: 수익성이 없는 익스체인지는 정리됐다. Wharton은 실패 원인으로 "breakthrough" 시장과 "re-formed" 시장을 혼동한 점을 꼽는다 — [Wharton, Surviving the shakeout](https://knowledge.wharton.upenn.edu/article/surviving-the-shakeout-where-b2b-exchanges-went-wrong/); [Computerworld](https://www.computerworld.com/article/1570797/exchanges-shift-gears.html)
- 수직형 쐐기 사례(포장): 유럽 Packmatic은 SaaS 기반 B2B 포장 마켓플레이스로 €15M을 유치했고 업계를 "불투명하고 낡은 산업"이라 부른다 — [Packaging Insights](https://www.packaginginsights.com/news/packmatic-secures-€15m-funding-to-accelerate-europes-opaque-and-outdated-industry.html). Packhelp(맞춤 인쇄 박스)는 Series B를 유치했다 — [TechCrunch 2021](https://techcrunch.com/2021/11/18/packhelp-series-b/amp/)
- 수직형 쐐기 사례(제조): Xometry 마켓플레이스 매출총이익률은 2025 Q2 35.4%, Q3 35.7%, 연간 34.7%(2024년 33.5%)이고, 4년 전에는 약 25%였다. 경영진은 가격 책정·매칭 알고리즘과 데이터 네트워크 효과를 원인으로 든다 — [Xometry Q2 2025](https://investors.xometry.com/news-releases/news-release-details/xometry-reports-record-second-quarter-2025-results); [Xometry Q3 2025](https://www.barchart.com/story/news/35886037/xometry-reports-record-third-quarter-2025-results); [3D Printing Industry, Q4 2025](https://3dprintingindustry.com/news/xometry-reports-record-q4-marketplace-revenue-and-improved-2025-results-249400/)

### Inferences
- "모든 위탁업체 매칭"을 표방하는 수평형 디렉터리는 피해야 한다. 업종 하나와 지역 하나에서 높은 매칭률과 재구매를 증명한 뒤 인접 업종(예: 박스 → 완충재 → 파렛트 → 3PL)으로 넓히는 것이 근거에 맞는다.
- Xometry 모델(플랫폼이 견적가를 정하고 공급자에게 재발주하는 리셀러형)은 30%대 마진을 증명했다. BU 하이브리드 논문의 결론과 마찬가지로 리셀러형은 누수를 구조적으로 막는다. 다만 운전자본과 품질 책임이 생긴다.

### Gaps
- 한국 수평형 B2B 디렉터리(예: 각종 "업체 찾기" 포털)의 실패/정체를 정량화한 국내 자료는 찾지 못했다.

## 4. 업종 선정 기준과 한국 후보 업종 평가

### Takeaway
기준은 거래 빈도, 객단가, 사양 표준화, 공급자 파편화, 신뢰 문제다. 평가 결과 첫 쐐기로 가장 유력한 후보는 산업포장(맞춤 골판지 박스·목포장·파렛트)이다. 사양을 표준화할 수 있고(치수·재질·수량), 반복 발주가 있으며, 공급자가 파편화돼 있고, 국내에 선행 투자 사례가 있다. 3PL은 수요는 크지만 로지켓 등 경쟁자가 있고 단골 관계가 형성된 뒤 누수가 크다. 금속/CNC는 캐파·Xometry형 경쟁이 이미 있다. 인력파견은 규제 리스크 때문에 제외하는 것이 좋다.

### Cited Findings
- 포장: 리우(포장포스·포장보스, 2017년 설립)는 소상공인 포장재 컨설팅과 생산업체 연결 중개를 한다. 약 20억원 시리즈A를 받았고 한솔제지가 유일한 전략적 투자자다 — [Dealsite 2022](https://dealsite.co.kr/articles/89090)
- 포장: 패커티브는 맞춤 박스 실시간 자동 견적(기존에는 문의 후 평균 1일 대기)과 50개부터 가능한 소량 제작을 출시했다 — [NextUnicorn newsroom](https://www.nextunicorn.kr/newsroom/e82561cd1e018169)
- 포장: 골판지 박스 제조사 창마루는 원래 기업 대상 B2B 영업(규격·배합 맞춤 견적)을 하다가 B2C 온라인 판매로 전환했다 — [Byline Network](https://byline.network/2020/08/18-99/)
- 3PL: 로지켓은 화주가 카테고리, 화물 특성, 월 물동량을 올리면 여러 물류사가 견적을 내는 역경매형 비교견적 플랫폼이다. 견적요청 중 냉장·냉동이 약 80%라고 밝혔다. 2021년에는 물류사 검색 "로지서치"를 출시했다 — [Byline Network](https://byline.network/?p=58293); [MT 2021](https://www.mt.co.kr/future/2021/05/11/2021042816482442299)
- 3PL(해외): WareMatch는 3PL에 마케팅 도구와 실시간 가격 기능을 주는 방식으로 $2M을 조달했다 — [Inside Logistics](https://www.insidelogistics.ca/?p=105139)
- 금속/CNC: 캐파는 약 2,000개 파트너, 도면 기반 RFQ, 에스크로 결제를 갖췄다 — [Tech42](https://www.tech42.co.kr/?p=15953)
- 화장품 OEM: 넥스트팬지아는 한국 ODM·OEM사의 해외 영업을 연결하고 해외 바이어 약 2천 곳을 확보했다고 밝혔다 — [CNC News](https://www.cncnews.co.kr/news/article.html?no=9257). 중소 뷰티 브랜드 성장 배경으로 한국콜마·코스맥스 같은 대형 ODM과 올리브영 성장이 꼽힌다 — [Bain Korea 2024](https://www.bain.com/ko/about-bain/media-center/bain-in-the-news/korea/2024/24.0322222.22-k-beauty-1). 크몽 등에서는 개인 컨설턴트가 제조사 매칭을 서비스로 판다 — [kmong](https://kmong.com/gig/181807)
- 청소·시설관리: 견적이 현장 확인(평수, 오염도, 인력, 장비)에 의존한다 — [숨고 업체 프로필](https://soomgo.com/profile/users/15373049). 미소는 시간 단위 정액 상품으로 견적 과정을 없앴다 — [miso.kr/officeclean](https://miso.kr/officeclean). 에이엠피엠(시설관리·미화 용역)과 클린버스 등 기존 업체가 있다 — [thevc 에이엠피엠](https://thevc.kr/ampm/products)

### 업종 평가 매트릭스 (Inference, 위 근거와 일반 업계 지식을 바탕으로 한 정성 평가: H=유리, M=보통, L=불리)

| 업종 | 거래 빈도 | 객단가 | 사양 표준화 | 공급자 파편화 | 신뢰 문제 | 누수 위험 | 경쟁 | 종합 |
|---|---|---|---|---|---|---|---|---|
| 산업포장(골판지 박스·목포장·파렛트) | H (소모품, 반복 발주) | M (수십만~수천만원) | H (치수·재질·수량·인쇄) | H (영세 지역 공장) | M (납기·품질 편차) | M~H (반복 발주라 짝이 형성됨) | M (리우·패커티브는 소상공인 중심, 산업용 목포장·파렛트는 공백 가능성) | 1순위 |
| 3PL/물류 | M (계약은 저빈도, 운영은 고빈도) | H | M (SKU·물동량·온도대) | H | H | H (계약 후 직거래) | M~H (로지켓, 각 풀필먼트 자체 영업) | 2순위 (리드 과금형이 적합) |
| 금속/CNC 가공 | M | M~H | M (도면 기반, 공차 해석 필요) | H | H | M | H (캐파, 글로벌 Xometry) | 비추천(정면 경쟁) |
| 화장품·식품 OEM | L (브랜드당 연 수회) | H | L (처방·인증·MOQ 협의) | M (대형 ODM 과점 + 소형 다수) | H | H | M | 관리형 컨설팅형만 가능 |
| 인쇄·판촉물 | H | L~M | H | H | M | M | H (레드프린팅 등 온라인 인쇄몰이 성숙, 본 조사에서 미검증) | 마진 압박 |
| 청소·시설관리 용역 | H (정기) | M | M (현장 실사 필요) | H | M | H (정기계약 후 직거래) | H (숨고·미소 등) | 비추천 |
| 인력파견 | H | M | M | M | H | H | H | 제외 (파견법 허가/규제, 미검증 — Gaps 참조) |

### Inferences
- 산업포장을 첫 쐐기로 추천한다. 이유는 (a) 반복 소모품이라 재구매 지표를 빨리 검증할 수 있고, (b) 사양이 구조화되어 RFQ 폼과 자동 견적으로 가기 쉽고, (c) 팩토리온 업종코드로 공급자 리스트를 만들 수 있고, (d) 국내 투자 사례(리우-한솔제지 SI, 패커티브)가 수요가 있다는 신호이고, (e) 기존 플레이어가 소상공인 소량 박스에 몰려 있어 중소 제조사·수출 기업용 목포장·파렛트·대량 골판지는 비어 있을 가능성이 있다(확인 필요).
- 3PL은 리드/견적 열람 과금이 맞는 2순위 업종이다(계약 이후 관계는 플랫폼 밖에서 이어지기 때문).
- 수출 포장(목포장, 훈증 ISPM-15 파렛트)은 수출바우처 물류 분야와 연결될 수 있다(4~6절 참조).

### Gaps
- 업종별 국내 시장 규모, 평균 객단가, 발주 빈도를 다룬 통계는 이번에 확보하지 못했다.
- 산업용 목포장·파렛트 전용 국내 B2B 플랫폼이 있는지는 확인하지 못했다(검색 결과 없음 ≠ 부재).
- 인력파견: 근로자파견법상 허가·업종 제한이 매칭 플랫폼에 어떻게 적용되는지는 1차 출처로 확인하지 못했다. 법률 검토가 필요하다.
- 인쇄 업종의 국내 온라인 인쇄몰 경쟁 강도는 이번 검색에서 직접 확인하지 못했다.

## 5. 수익 모델 비교와 B2B 수수료율

### Takeaway
수수료율은 (1) 새 수요를 만들어 주는지, (2) 공급자에게 주는 편의, (3) 경쟁 강도에 따라 정해진다. 누수가 큰 저빈도 B2B 서비스에서는 거래 수수료보다 견적 발송/열람 과금(숨고형)이 실제로 작동했다. 관리형/리셀러형(Xometry)은 30%대 마진을 내지만 운영 부담이 크다. 금융(BNPL/외상거래)은 수익원이면서 누수 방어 수단이다.

### Cited Findings
- Lenny Rachitsky의 마켓플레이스·플랫폼 40곳 수수료율 분석(2021): 차이는 주로 신규 수요 창출 능력, 판매자에게 주는 편의, 시장 경쟁 강도에서 나온다(원문은 유료) — [Lenny thread](https://threadreaderapp.com/thread/1386706274037891075); [Lenny's Newsletter, Choosing a take rate](https://www.lennysnewsletter.com/p/take-rates)
- 수수료율이 높을수록 거래량은 대체로 줄어든다. Udemy는 자체 판매 강의와 플랫폼 판매 강의에 다른 수수료를 매긴다(유입 경로별 차등 수수료) — [TechCrunch 2021, 4 strategies for setting marketplace take rates](https://techcrunch.com/2021/11/17/4-strategies-for-setting-marketplace-take-rates/)
- 관리형 마켓은 수수료율이 높지만 운영비 부담이 크다 — [a16z glossary](https://a16z.com/the-marketplace-glossary/)
- 리셀러/관리형 제조 마켓 벤치마크: Xometry 마켓플레이스 매출총이익률은 약 35%(2025)다. 공급자 서비스(광고·SaaS 등) 부문의 마진은 약 88~89%지만 매출이 줄고 있다(2025 FY 약 -5%) — [3D Printing Industry](https://3dprintingindustry.com/news/xometry-reports-record-q4-marketplace-revenue-and-improved-2025-results-249400/); [Xometry IR](https://investors.xometry.com/news-releases/news-release-details/xometry-reports-record-second-quarter-2025-results)
- 숨고(견적 발송 과금): 고수 가입은 무료이고 견적을 보낼 때 비용이 든다. 고객이 견적을 열람했을 때만 과금되고, 48시간 안에 열람되지 않으면 보너스캐시로 돌려준다 — [숨고 고수 안내](https://soomgo.com/pro). 2020년 2월 크레딧에서 캐시로 정책을 바꾸면서 고수 반발이 있었다 — [일간스포츠 2020](https://isplus.com/article/view/isp202004240015). 단가는 출처마다 다르다. 건당 3,000~4,000원(데모데이 분석: 고수 200만, 매출 624억, 10년 만에 흑자)이라는 자료가 있고 — [Demoday BM analysis](https://demoday.co.kr/bm-analysis/104) — 1,000~5,000포인트(약 1만~5만원)라는 블로그도 있다 — [wikidocs blog](https://wikidocs.net/blog/@knarchive/26221/). 같은 분석은 고수들이 이를 마케팅 비용으로 받아들였다고 평가한다.
- 결제/에스크로 수수료 참고: 번개페이 3.5%(판매자 부담) — [요즘IT](https://yozm.wishket.com/magazine/detail/2710/); 캐파결제는 출시 프로모션으로 수수료 0원 — [Tech42](https://www.tech42.co.kr/?p=72198)
- 금융: B2B BNPL/외상거래는 구매자 유지 도구로 제시된다(벤더 주장) — [Hokodo](https://www.hokodo.co/resources/how-to-prevent-disintermediation-on-your-b2b-marketplace); NFX도 "fintech-enabled marketplaces" 운영 매뉴얼을 냈다(원문 미확인) — [NFX](https://www.nfx.com/post/new-operating-manual-fintech-enabled-marketplaces)
- SaaS 기반 B2B 마켓 사례로 Packmatic(포장)이 있다 — [Packaging Insights](https://www.packaginginsights.com/news/packmatic-secures-€15m-funding-to-accelerate-europes-opaque-and-outdated-industry.html)

### 수익 모델 비교 (Inference)

| 모델 | 장점 | 단점/리스크 | 적합 단계 |
|---|---|---|---|
| 거래 수수료(take rate) | GMV에 연동되어 확장성이 높음 | 반복 발주 누수, 결제를 플랫폼에 묶어야 함 | 에스크로·외상거래를 갖춘 뒤 |
| 관리형/리셀러 마진 | 누수를 구조적으로 차단, 마진 약 30%대(Xometry) | 운전자본, 품질·클레임 책임, 운영 인력 | MVP(컨시어지)에서 자연스럽게 시작 |
| 공급자 구독/리드 과금 | 누수와 무관하게 매출 발생, 국내 수용성 검증(숨고) | 리드 품질이 나쁘면 공급자 이탈, 정책 변경 시 반발 | 수요가 충분해진 뒤 |
| 견적 열람/발송권 | 공급자 마케팅비로 인식됨, 미열람 환불로 공정성 확보 | 저빈도·고단가 B2B에서는 단가 설정이 어려움 | 3PL 같은 계약형 업종 |
| 광고/상위 노출 | 마진이 높음 | 트래픽 규모가 필요, 신뢰 훼손 가능 | 후기 |
| SaaS(견적·발주·재고) | 끈끈함, 공급 확보 | 국내 영세 공장의 지불 의사가 낮음(가정) | 무료 도구로 공급 확보 |
| 금융(BNPL/팩토링) | 누수 방어 + 수익 | 신용 리스크, 제휴 금융사 필요 | 거래 데이터가 쌓인 뒤 |

### Gaps
- 국내 B2B 제조/서비스 마켓의 공개된 거래 수수료율(예: 위시켓 개발 외주 수수료, 캐파 현 수수료)은 이번 검색에서 확인하지 못했다. 위시켓 대표 인터뷰도 찾지 못했다.
- 국내 B2B BNPL 제휴 사례(예: 핀테크 외상결제 서비스)는 조사하지 못했다.
- Lenny 40개사 수수료율 표의 실제 수치는 유료라 미확인이다.

## 6. 한국 특화 GTM: 정부지원, 산단, 전시회, 검색광고

### Takeaway
정부 바우처(수출바우처, 혁신바우처)는 공급자/플랫폼이 "수행기관/공급기업"으로 등록해 바우처 예산으로 매출을 받을 수 있는 채널이다. 수요기업을 모으는 통로이기도 하다. 수출바우처는 14개 분야, 약 7,500개 수행기관 규모다. 혁신바우처는 제조 중소기업 대상 컨설팅·기술지원·마케팅을 기업당 최대 5천만원까지 지원한다. 산단 공장 데이터는 공개돼 있다. 네이버 B2B 키워드의 CPC 실측치는 확보하지 못했다.

### Cited Findings
- 수출바우처: 2026년 기준 14개 분야에서 플랫폼에 등록된 약 7,500개 수행기관 서비스 중 기업이 골라 쓰는 우산형 제도다. 2026 일반 물류바우처(2차) 참여기업 모집은 2026-07-31 마감이었다. 긴급지원바우처 4차는 2026-12-31까지 서비스를 마치고 정산 요청을 해야 한다 — [MOTIR 공고 첨부](https://www.motir.go.kr/attach/down/c26df36c4f964b1523b31be51e734922/13c5e58bcd5af6d60662932f793a9294/778bdbf5db9ced7c8fd52756c00bf0cd); [KOTRA 2026 공고](https://kotra.or.kr/upload/2026/10/27/BM202610270000113185_0.pdf); [korea.kr](https://www.korea.kr/multi/visualNewsView.do?newsId=148956276)
- 혁신바우처(중기부): 제조 중소기업에 컨설팅·기술지원·마케팅을 패키지로 제공하며 2020년에 시작했다. 2026년 1차 공고는 기업당 최대 5천만원이고 비수도권 인구감소지역 지원을 강화했다. 지역제조 별도 공고도 있다 — [korea.kr 정책뉴스](https://m.korea.kr/news/policyNewsView.do?newsId=148954562); [2026 혁신바우처(지역제조) 공고 PDF](https://grant-documents.thevc.kr/294687_(%EC%A0%9C2026-194%ED%98%B8)_2026%EB%85%84_%EC%A4%91%EC%86%8C%EA%B8%B0%EC%97%85_%ED%98%81%EC%8B%A0%EB%B0%94%EC%9A%B0%EC%B2%98(%EC%A7%80%EC%97%AD%EC%A0%9C%EC%A1%B0)_%EC%82%AC%EC%97%85_%EC%A7%80%EC%9B%90%EA%B3%84%ED%9A%8D_%EA%B3%B5%EA%B3%A0.pdf); [TIPA 공고](https://www.tipa.or.kr/s040101/file_down/id/20791); [data.go.kr 혁신바우처 데이터](https://www.data.go.kr/data/15150977/fileData.do)
- 산업단지: 산단별 공장 데이터(업체 수, 공장 유형, 고용인원)를 공개한다 — [data.go.kr](https://www.data.go.kr/data/15127209/fileData.do)
- 네이버 검색광고: CPC는 비공개 경매이고 품질지수가 반영된다. 대행사 기준 일반 예산은 소상공인 월 30~100만원, 중견 규모는 월 수백만원이다(업종 미특정, 대행사 홍보 자료) — [i-boss](https://www.i-boss.co.kr/ab-2987-545677). B2B 검색광고는 클릭 수보다 검색 의도와 랜딩이 맞는지가 중요하다 — [AMPM insight](https://inside.ampm.co.kr/insight/13284)

### Inferences
- 플랫폼 운영사가 (a) 혁신바우처 마케팅 분야 공급기업, (b) 수출바우처 물류/디자인(포장 디자인) 분야 수행기관으로 등록할 수 있다면, 수요기업이 바우처로 결제하는 구조를 만들 수 있다. 등록 요건부터 확인해야 한다.
- 수출 목포장·ISPM-15 파렛트 수요는 수출 중소기업에 집중되므로 KOTRA·무역협회·지역 수출지원센터와 공동 프로모션하는 채널이 그럴듯하다.
- 네이버 CPC는 검색광고 키워드 도구로 실측해야 한다(예: "목포장", "파렛트 제작", "골판지 박스 제작", "3PL 업체"). 롱테일 지역+품목 조합("반월 목포장")이 효율적일 것이라는 가정은 검증이 필요하다.

### Gaps
- 혁신바우처 공급기업과 수출바우처 수행기관의 신규 등록 자격·일정(2027년도)은 확인하지 못했다. TIPA, 수출바우처 포털 공고를 직접 확인해야 한다.
- 스마트공장 지원사업을 이 사업 GTM에 어떻게 연결할지는 조사하지 못했다.
- 산업단지 협회(예: 산단 경영자협의회)와의 제휴 사례, 포장 관련 전시회(예: 코리아팩) 참가 비용·효과 자료는 확보하지 못했다.
- 네이버 B2B 키워드의 실제 CPC 수치는 공개 출처에서 찾지 못했다.

## 7. MVP 범위와 추적 지표

### Takeaway
린 MVP는 업종 하나, 지역 하나에서 구조화된 RFQ 폼, 사람이 직접 하는 컨시어지 매칭(3~5곳 견적 수집), 검증 배지(사업자·공장등록·현장 실사)로 구성한다. 결제는 처음에 수동 에스크로나 플랫폼 명의 발주(리셀러형)로 시작한다. 핵심 지표는 RFQ→견적 수령→계약 전환율, 견적 응답 시간, 재구매율, 매칭된 쌍의 플랫폼 경유 재주문율이다. Tavel의 "Happy GMV" 관점을 따른다.

### Cited Findings
- 작고 제한된 시장에서 먼저 "minimum viable happiness"를 달성한다. Happy GMV가 핵심이다 — [Sarah Tavel](https://sarahtavel.medium.com/the-hierarchy-of-marketplaces-introduction-and-level-1-983995aa218e)
- a16z 마켓플레이스 13개 지표(유동성, 매칭률, 재구매/코호트, 테이크레이트 등) 프레임워크가 있다 — [a16z, 13 metrics for marketplace companies](https://a16z.com/2020/02/21/13-metrics-for-marketplace-companies); [a16z, marketplace engagement](https://a16z.com/2020/02/20/marketplace-engagement/)
- Lenny의 "가장 중요한 마켓플레이스 지표" 글(2022)은 유료라 원문을 확인하지 못했다 — [Lenny's Newsletter](https://www.lennysnewsletter.com/p/the-most-important-marketplace-metrics?open=false)
- 국내 선례: 캐파 초기 관리형(게이트키핑+제조 대행) → RFQ 알림 + 1차 견적 비교 → 에스크로 결제 → 안심번호 순서였다 — [Tech42](https://www.tech42.co.kr/?p=15953); [Tech42 캐파결제](https://www.tech42.co.kr/?p=68611)
- 포장 업종의 핵심 불편은 견적 대기(평균 1일)와 MOQ다. 패커티브는 실시간 자동 견적과 50개 소량 제작으로 이를 풀었다 — [NextUnicorn](https://www.nextunicorn.kr/newsroom/e82561cd1e018169)
- 숨고는 미열람 견적을 환불해 공급자 측 공정성을 확보한다(리드 과금으로 넘어갈 때 참고) — [숨고 고수 안내](https://soomgo.com/pro)

### Inferences (MVP 설계 제안)
- 범위: 산업포장(골판지 박스 + 목포장/파렛트), 수도권 서남부 산단(예: 반월·시화) 또는 한 개 광역권. 공급자 30~50곳을 직접 실사·검증한다.
- 기능: (1) 구조화된 RFQ 폼(치수, 재질/골 종류, 인쇄 도수, 수량, 납기, 수출 여부·ISPM-15), (2) 운영자가 24시간 안에 3곳 견적을 모아 비교표 제공, (3) 검증 배지(사업자등록, 팩토리온 공장등록 여부, 현장 사진, 납기 준수 이력), (4) 연락처 마스킹, (5) 수동 에스크로 또는 플랫폼 명의 발주로 마진 확보, (6) 재주문 원클릭(이전 사양 복제)으로 반복 발주를 플랫폼에 묶어 둠.
- 지표: RFQ 수/주, RFQ당 견적 수와 첫 견적까지 시간, 견적→계약 전환율, 계약 GMV와 마진, 90일 재구매율(구매자), 매칭 쌍의 플랫폼 경유 재주문율(누수 대리 지표), 공급자 견적 응답률, 클레임·납기 지연율, NPS.
- 수익 순서: 컨시어지 마진(리셀러형) → 에스크로 수수료 + 외상결제 → 공급자 프리미엄(검증 배지·상위 노출·견적 도구 SaaS).

### Gaps
- 국내 B2B RFQ 마켓의 공개된 전환율 벤치마크(RFQ→계약)는 찾지 못했다.
- 캐파·로지켓의 재구매율 데이터는 공개 자료에서 확인되지 않았다.
