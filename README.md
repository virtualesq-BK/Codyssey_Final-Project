# Codyssey_Final-Project
GitHub 리포지토리에서 다른 팀원(Contributor)을 초대하여 공동 작업을 진행하려면 아래의 순서대로 설정해 주시면 됩니다.1.Settings 메뉴 이동:상단 메뉴 탭의 맨 오른쪽에 있는 Settings 버튼을 클릭합니다.2.Collaborators 메뉴 선택:왼쪽 사이드바 메뉴 중 Access 섹션 아래에 있는 Collaborators를 클릭합니다.3.비밀번호 인증 (필요 시):보안 확인 요청 창이 떠오르면 GitHub 계정 비밀번호나 2단계 인증(2FA)을 진행합니다.4.팀원 초대:Add people 버튼을 누른 후, 초청하려는 팀원의 GitHub 아이디(Username) 또는 이메일 주소를 입력하여 초대장을 전송합니다.초대받은 사용자(Contributor)가 초청 이메일 또는 GitHub 알림을 확인하고 승인(Accept)하면 즉시 해당 리포지토리에에 접근 및 커밋/푸시 권한을 갖게 됩니다.


# GitHub에 팀 전체가 공유할 기준 구조 생성 => "develop"

# 이후 작업 순서

## 1. 이제부터 5명(A~E)이 Branch를 만듭니다

각 팀원은 develop에서 최신 코드를 받은 후 자신의 Branch를 만듭니다.

A
git checkout develop
git pull
git checkout -b feature/orchestrator-decision

B
git checkout develop
git pull
git checkout -b feature/market-competitor-rag

C
git checkout develop
git pull
git checkout -b feature/customer-business-model

D
git checkout develop
git pull
git checkout -b feature/financial-risk

E
git checkout develop
git pull
git checkout -b feature/platform

## 2. 각자 코딩 툴(예: Claude Code)을 사용하는 방식

예를 들어 B가 Market/Competitor 담당이라면 Claude Code에게:

"나는 Market Agent와 Competitor Agent 담당이다. 현재 Repository의 docs/agent-interface.md와 domain/agent_result.py를 먼저 읽고, 공통 인터페이스를 변경하지 않는 범위에서 Market Agent를 구현해라."

라고 지시합니다.

중요한 것은 Claude Code에게 "공통 인터페이스를 바꾸지 말라"고 명시하는 것입니다.

만약 B가:

"AgentResult에 market_score를 추가하면 좋겠다."

라고 생각하면 직접 수정하지 않고 GitHub Issue를 만듭니다.

Issue #27
[Architecture] AgentResult에 market_score 필드 추가 검토

A가 검토하고 팀에서 결정합니다.

## 3. PR은 이렇게 진행

B가 Market Agent를 완성했다면:

git add .
git commit -m "feat: implement market agent"
git push origin feature/market-competitor-rag

GitHub에서:

feature/market-competitor-rag
             ↓
          Pull Request
             ↓
          develop

으로 PR을 만듭니다.

PR 설명에는:

## 작업 내용
- Market Agent 구현
- Market prompt 구현
- RAG 연동
- Unit test 추가

## 테스트
- pytest tests/agents/test_market_agent.py

## 관련 Issue
#12

정도로 작성합니다.

## 4. 절대로 각자의 Branch를 main에 바로 Merge하지 않습니다

권장 구조:

feature/*
     ↓
    PR
     ↓
 develop
     ↓
Integration Test
     ↓
    PR
     ↓
   main

입니다.

main = 항상 배포 가능한 코드

라는 원칙을 유지하세요.

## 5. 5명 병렬 개발에서 특히 중요한 규칙
Rule 1

domain/과 services/의 공통 Interface는 함부로 수정하지 않는다.

Rule 2

Agent 담당자는 자기 Agent 폴더를 중심으로 개발한다.

Rule 3

공통 변경이 필요하면 GitHub Issue를 만든다.

Rule 4

PR을 올릴 때 반드시 자기 Agent 테스트를 포함한다.

Rule 5

develop에 Merge하기 전에 다른 팀원 1명이 Code Review한다.

## 6. 최종적으로 GitHub에서 이렇게 흘러갑니다
                    GitHub
                      │
                   main
                      │
                   develop
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
    A Branch       B Branch       C Branch
       │              │              │
 Orchestrator    Market/RAG      Customer
 Decision        Competitor      BM
       │              │              │
       └──────────────┼──────────────┘
                      │
                     PR
                      ↓
                  develop
                      │
                 Integration
                      │
                      ▼
                    main
                      │
                      ▼
                   Deploy

## 7. 4주 전체 개발에서는 이렇게 연결하면 됩니다
┌──────────────┬──────────────────────────────────┐
│ 1주차        │ 설계 + Skeleton                  │
├──────────────┼──────────────────────────────────┤
│ 월           │ ★ Kick-off 전체회의             │
│ 화~수        │ 공통 Interface + 개발환경        │
│ 목           │ ★ Integration Meeting #1         │
│ 금           │ 전체 Skeleton 작동               │
├──────────────┼──────────────────────────────────┤
│ 2주차        │ Agent + RAG 개발                  │
├──────────────┼──────────────────────────────────┤
│ 월~수        │ 6개 Agent 병렬 개발              │
│ 목           │ ★ Integration Meeting #2         │
│ 금           │ ★ 첫 E2E Demo                   │
├──────────────┼──────────────────────────────────┤
│ 3주차        │ 통합 + Memory + 평가             │
├──────────────┼──────────────────────────────────┤
│ 월~수        │ RAG/Memory/Evaluation/UX         │
│ 목           │ ★ Integration Meeting #3         │
│ 금           │ 실제 사용자 테스트 시작          │
├──────────────┼──────────────────────────────────┤
│ 4주차        │ 안정화 + 사용자검증 + 발표        │
├──────────────┼──────────────────────────────────┤
│ 월           │ 사용자 피드백 분석               │
│ 화           │ ★ Feature Freeze                │
│ 수           │ Final E2E Test                  │
│ 목           │ ★ Final Integration Meeting     │
│ 금           │ 최종 발표/제출                   │
└──────────────┴──────────────────────────────────┘


5명이 "각자 코드를 만들고 마지막에 합치는 것"이 아닌, 

① 하나의 GitHub Repository → ② 공통 Schema/Interface 확정 → ③ 각자 Branch → ④ 독립 Agent 개발 → ⑤ PR → ⑥ Integration Test → ⑦ develop 통합 → ⑧ main 배포

입니다.

그리고 코딩툴은 각 팀원이 자기 Branch에서 사용하는 개발 도구이고, GitHub는 5명의 코드를 통합하고 버전을 관리하는 협업 기준점입니다.

이 구조로 시작하면 나중에 발표에서도 단순히 "AI Agent 8개를 만들었다"가 아니라 "공통 Agent Contract와 Provider abstraction을 설계하고, 5명이 병렬 개발한 Multi-Agent AI 시스템"이라는 개발 과정 자체를 포트폴리오로 보여줄 수 있습니다.
