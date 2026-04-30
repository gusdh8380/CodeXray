import { useState } from "react"
import { ChevronDown, ChevronRight, BookOpen } from "lucide-react"

export function EvaluationPhilosophyToggle() {
  const [open, setOpen] = useState(false)
  return (
    <div className="rounded-lg border bg-card">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-2.5 px-4 py-3 text-left hover:bg-muted/40 rounded-lg transition-colors"
      >
        {open ? (
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
        )}
        <BookOpen className="h-4 w-4 text-amber-700 dark:text-amber-400" />
        <span className="text-sm font-semibold">
          이 도구가 바이브코딩을 어떻게 평가하나요?
        </span>
      </button>
      {open && (
        <div className="px-6 pb-5 pt-1 space-y-6 text-sm leading-relaxed">
          <Section title="1. 한 줄 정의">
            <p>
              <strong>잘된 바이브코딩 프로젝트 = "주인이 있는 프로젝트".</strong>
            </p>
            <p>
              코드 품질이나 도구 셋업이 아니라,{" "}
              <em>사람이 이 프로젝트를 이끌고 있는가</em>가 핵심입니다.
            </p>
          </Section>

          <Section title='2. "주인이 있다" 의 운영 정의'>
            <p>다음 셋이 동시 성립할 때:</p>
            <ol className="list-decimal pl-5 space-y-1">
              <li>
                <strong>외부화된 의도</strong> — 의도가 글로 박혀 새 AI 세션이{" "}
                <em>맥락 없이도</em> 일을 이어받을 수 있다.
              </li>
              <li>
                <strong>독립 검증</strong> — 결과를 사용자가 손으로 (또는 실행·테스트로)
                직접 확인한 흔적이 있다.
              </li>
              <li>
                <strong>인간 최종 판단</strong> — 다음 결정은 사람이 내린다 (AI 추천이
                결정을 대체하지 않는다).
              </li>
            </ol>
            <p className="text-muted-foreground italic">
              이 셋 중 하나라도 무너지면 <em>코드가 좋아도</em> 프로젝트는 표류합니다.
            </p>
          </Section>

          <Section title="3. 8 가지 운영 신호 — 측정 6 + 자가 점검 2">
            <p>
              <strong>CodeXray 가 흔적으로 측정하는 6 가지:</strong>
            </p>
            <ol className="list-decimal pl-5 space-y-0.5 text-xs">
              <li>의도가 글로 박혀 있다 (CLAUDE.md, AGENTS.md 같은 AI 지속 지시 문서)</li>
              <li>의도와 비의도가 먼저 적힌다 (Not 섹션, ADR, decision log)</li>
              <li>손으로 검증한 흔적 (validation 디렉토리, screenshot, demo)</li>
              <li>재현 가능한 실행 경로 (build/test/run 명령어, env sample)</li>
              <li>실패에서 배운 흔적이 다음 변경에 반영 (회고 + 후속 변경)</li>
              <li>작게 쪼개고 이어갈 수 있다 (작은 PR, saved plans)</li>
            </ol>
            <p>
              <strong>CodeXray 가 못 보는 2 가지 — 사용자 자가 점검:</strong>
            </p>
            <ol start={7} className="list-decimal pl-5 space-y-0.5 text-xs">
              <li>사용자가 What/Why/Next 를 자기 입으로 설명할 수 있는가</li>
              <li>다음 행동의 우선순위를 사람이 정하고 있는가</li>
            </ol>
          </Section>

          <Section title="4. 3 축 매핑">
            <ul className="space-y-1 text-xs">
              <li>
                <strong>의도 (intent)</strong> — 신호 1·2: 외부화된 의도가 있는가
              </li>
              <li>
                <strong>검증 (verification)</strong> — 신호 3·4: 결과를 독립적으로
                확인할 수 있는가
              </li>
              <li>
                <strong>이어받기 (continuity)</strong> — 신호 5·6: 다음 세션이
                이어받을 수 있는가
              </li>
            </ul>
          </Section>

          <Section title="5. 4 단계 상태가 무슨 뜻인가">
            <p className="text-xs">
              <strong>0–100 점수는 보여주지 않습니다.</strong> "정확해 보이는 숫자"가
              사용자를 오해시키기 때문입니다. 대신 4 단계 상태:
            </p>
            <ul className="space-y-1 text-xs">
              <li>
                <strong>강함 (strong)</strong> — 신호 풀 70% 이상 + 핵심 신호 모두 충족
              </li>
              <li>
                <strong>보통 (moderate)</strong> — 신호 풀 40% 이상
              </li>
              <li>
                <strong>약함 (weak)</strong> — 신호 풀 10% 이상
              </li>
              <li>
                <strong>판단유보 (unknown)</strong> — 데이터 수집 실패 또는 모든 신호 0%
              </li>
            </ul>
            <p className="text-xs text-muted-foreground italic">
              축마다 신호 풀 크기가 다르므로 비율로 평가합니다.
            </p>
          </Section>

          <Section title="6. 다음 행동 카드는 왜 0–3 개로 변하는가">
            <p className="text-xs">
              다른 도구처럼 항상 카드 3 개를 채우지 않습니다.
            </p>
            <ul className="space-y-1 text-xs">
              <li>
                <em>고확신 추천 1 개</em> &gt; <em>저확신 추천 3 개</em> (선택 과부하·알람
                피로 연구)
              </li>
              <li>카드 강제 채움 = 가짜 노이즈</li>
              <li>다 잘 갖춘 프로젝트는 추천 0 개가 정직한 답</li>
            </ul>
          </Section>

          <Section title="7. 이 도구가 못 보는 것 — 항상 자가 점검">
            <p className="text-xs">
              화면 위쪽 결과와 <em>무관하게</em> 다음 4 가지는 코드만 봐서는 판단할 수
              없습니다:
            </p>
            <ol className="list-decimal pl-5 space-y-0.5 text-xs">
              <li>사용자(나)가 What/Why/Next 를 자기 입으로 설명할 수 있는가</li>
              <li>손으로 한 검증이 실제로 매번 굴러가는가</li>
              <li>다음 행동의 우선순위를 사람이 정하고 있는가</li>
              <li>
                외부 도구(Notion, Confluence, Slack, Linear 등)와 README 같은 문서의
                질적 깊이는 자동 판단 못 합니다
              </li>
            </ol>
            <p className="text-xs text-muted-foreground italic">
              결과 라벨이 좋아도 위 넷이 무너지면 프로젝트는 위험. 결과 라벨이 나빠도
              위 넷이 단단하면 프로젝트는 건강.
            </p>
          </Section>

          <Section title="8. 평가 기준의 출처">
            <p className="text-xs">
              이 평가 방법은 다음 공개 자료의 권고를 종합한 결과입니다:
            </p>
            <ul className="text-xs space-y-0.5">
              <li>
                <strong>Anthropic</strong> — Claude Code Best Practices (CLAUDE.md 의 역할)
              </li>
              <li>
                <strong>OpenAI</strong> — Codex AGENTS.md guide, PLANS.md / ExecPlan format
              </li>
              <li>
                <strong>Andrej Karpathy</strong> — vibe coding 용어의 출처. 인간 미감과
                판단의 필요성
              </li>
              <li>
                <strong>Simon Willison</strong> — "Context is king", "Tests are
                non-negotiable"
              </li>
              <li>
                <strong>Kent Beck</strong> — Constrain Context, Preserve Optionality,
                Maintain Human Judgment
              </li>
              <li>
                <strong>Geoffrey Huntley</strong> — "한 번에 한 가지, 매 루프마다 계획"
              </li>
              <li>
                <strong>Birgitta Böckeler (Thoughtworks)</strong> — "AI is an
                accelerator, not an automator"
              </li>
              <li>
                <strong>Will Larson</strong> — Theory of improvement (점수의 한계)
              </li>
              <li>
                <strong>GitHub Spec Kit</strong> — intent-driven development
              </li>
              <li>
                <strong>Cursor / Cline / Aider</strong> — Plan Mode, Memory Bank, /undo
                패턴
              </li>
            </ul>
          </Section>
        </div>
      )}
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-2">
      <h4 className="text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-400">
        {title}
      </h4>
      <div className="space-y-2">{children}</div>
    </div>
  )
}
