"""Regression checks for the agent-native bootstrap and history loop contract."""

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


class AgentNativeBootstrapContractTests(unittest.TestCase):
    def test_public_flow_does_not_offer_removed_bootstrap_cli(self) -> None:
        removed_entry = "jarvis-box " + "bootstrap jarvis"
        removed_resume = "bootstrap " + "--resume"
        offenders: list[str] = []
        for path in REPO_ROOT.rglob("*"):
            if (
                not path.is_file()
                or ".git" in path.parts
                or path.suffix not in {".md", ".sh"}
            ):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if removed_entry in text or removed_resume in text:
                offenders.append(str(path.relative_to(REPO_ROOT)))
        self.assertEqual(offenders, [])

    def test_agent_native_prompt_keeps_human_questions_irreducible(self) -> None:
        text = _read("playbooks/prompts/agent-native-bootstrap.md")
        self.assertIn("不要先向我发一份长表单", text)
        self.assertIn("授权范围或身份冲突", text)
        self.assertIn("不要让我新开 session", text)
        self.assertIn("按 Phase 3-14 推进", text)

    def test_phase_3_records_uid_and_ownership_instead_of_blind_escalation(self) -> None:
        text = _read("playbooks/phases/phase-03-bootstrap-invocation.md")
        self.assertIn("有效 UID/GID", text)
        self.assertIn("service-private state", text)
        self.assertIn("host UID/GID mapping", text)
        self.assertIn("JARVIS_WORKSPACE_ROOT", text)
        self.assertIn("不盲目执行 `sudo`", text)

    def test_phase_6_orchestration_never_makes_customer_relay_agents(self) -> None:
        text = _read("playbooks/phases/phase-06-business-discovery.md")
        self.assertIn("agent-owned 全生态扫描编排", text)
        self.assertIn("不要求客户新开 session", text)
        self.assertIn("没有并发能力时按同一 lane contract 顺序执行", text)
        self.assertIn("Phase 7 骨架在此时尚未被假定存在", text)
        self.assertNotIn("用户复制到新 session", text)

    def test_history_calibration_is_a_per_group_control_loop(self) -> None:
        phase = _read("playbooks/phases/phase-12-history-replay.md")
        prompt = _read("playbooks/prompts/history-calibration.md")
        repo_reference = _read(
            "templates/repo-local-skill/skills/references/history-replay-loop.md"
        )
        company_reference = _read(
            "templates/company-jarvis/repo/references/history-replay.md"
        )
        surfaces = (phase, prompt, repo_reference, company_reference)
        for text in surfaces:
            self.assertIn("cursor", text)
            self.assertIn("preconsumed_commits", text)
            self.assertIn("skill-creator", text)
            self.assertIn("calibration_skill_ref", text)
            self.assertIn("authoritative", text)
        self.assertIn("same-case rerun", phase)
        self.assertIn("同 case", prompt)
        self.assertIn("Same-Case Rerun", repo_reference)
        self.assertIn("Same-case rerun", company_reference)
        combined = "\n".join(surfaces)
        self.assertIn("禁止先把整个时间范围分流完", phase)
        self.assertIn("不要先把整个时间范围的 commits 全量语义分类", prompt)
        self.assertIn("不先做全量语义分类", repo_reference)
        self.assertIn("不要先把整个时间范围分类", company_reference)
        self.assertIn("不得创建名为 `eval-loop` 的 skill", phase)
        self.assertNotIn("连续 N 个 commit 组", phase)
        self.assertNotIn("将 commits 按类型分流", phase)
        self.assertNotIn("80→200→500", combined)

        ordering_checks = (
            (phase, "先持久化 baseline ref", "再推进 cursor"),
            (prompt, "先持久化新的 `calibration_skill_ref`", "再推进 cursor"),
            (repo_reference, "持久化 baseline before/after", "再推进 cursor"),
            (company_reference, "先持久化累计 ref", "再推进 cursor"),
        )
        for text, promotion, advance in ordering_checks:
            self.assertLess(text.index(promotion), text.index(advance))

    def test_history_scope_distinguishes_seed_from_full_range(self) -> None:
        phase = _read("playbooks/phases/phase-12-history-replay.md")
        checklist = _read("playbooks/phase-checklist.md")
        prompt = _read("playbooks/prompts/history-calibration.md")
        self.assertIn("`seed`", phase)
        self.assertIn("`full-range`", phase)
        self.assertIn("`seed completed`", checklist)
        self.assertIn("`full-range completed`", checklist)
        self.assertIn("不能因上下文/预算自动降级成 seed", checklist)
        self.assertIn("cursor 越过时间边界前都继续", prompt)

    def test_history_templates_use_primary_attribution_before_failure_dimension(self) -> None:
        reference = _read(
            "templates/repo-local-skill/skills/references/history-replay-loop.md"
        )
        self_improve = _read(
            "templates/repo-local-skill/skills/self-skills-improve/SKILL.md"
        )
        for text in (reference, self_improve):
            self.assertIn("Primary Attribution", text)
            self.assertIn("`skill_gap`", text)
            self.assertIn("`source_access_environment`", text)
            self.assertIn("`no_skill_gap` 是", text)
        self.assertIn("writable calibration snapshot", self_improve)
        self.assertIn("Phase 13 才按 ordered candidate set", self_improve)
        self.assertIn("最终累计 authoritative snapshot", self_improve)

    def test_repo_local_package_does_not_generate_eval_loop_skill(self) -> None:
        self.assertFalse(
            (REPO_ROOT / "templates/repo-local-skill/skills/eval-loop.md").exists()
        )
        instantiator = _read("scripts/instantiate_repo_local_skill.py")
        verifier = _read("scripts/verify_bootstrap_output.py")
        generated_name = "eval-" + "loop.md"
        canonical_manifest = instantiator.split("CANONICAL_FILES =", 1)[1].split("]", 1)[0]
        required_manifest = verifier.split("REQUIRED_REPO_SKILL_FILES =", 1)[1].split("]", 1)[0]
        self.assertNotIn(generated_name, canonical_manifest)
        self.assertNotIn(generated_name, required_manifest)
        self.assertIn("LEGACY_EVAL_LOOP_TEMPLATE_SHA256", instantiator)
        self.assertIn("legacy_eval_loop_skill_present", verifier)

    def test_e2e_invokes_runtime_agent_directly(self) -> None:
        controlled = _read("scripts/run_customer_bootstrap_e2e.sh")
        apple = _read("e2e/apple-container-claude/run-in-container.sh")
        self.assertIn("running controlled runtime agent directly", controlled)
        self.assertIn("/e2e/bootstrap-agent", controlled)
        self.assertIn("running real Claude directly with create-jarvis-skill", apple)
        self.assertIn("/e2e/claude-bootstrap-agent", apple)
        self.assertIn("playbooks/prompts/agent-native-bootstrap.md", apple)
        self.assertNotIn("chmod -R a+rwx", controlled)
        self.assertIn("resolve_e2e_agent_user.sh", controlled)
        self.assertIn(r'runuser -u \"\$runtime_agent_user\"', controlled)
        self.assertIn("/e2e/runtime-agent-user", controlled)
        self.assertIn("JARVIS_WORKSPACE_ROOT=/e2e/work/bootstrap", controlled)
        self.assertIn(
            "agent user must not own service-private /var/lib/jarvis-box", controlled
        )
        self.assertNotIn("continuing to verifier", controlled)


if __name__ == "__main__":
    unittest.main()
