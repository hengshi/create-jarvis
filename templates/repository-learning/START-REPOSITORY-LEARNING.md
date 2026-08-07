# Start Repository Learning — `{{REPOSITORY_NAME}}`

This is the complete entry pointer for one clean top-level Codex process. Do not execute another repository card in this chat.

## Fixed scope

- Construction Workspace: `{{CONSTRUCTION_WORKSPACE}}`
- Build context: `{{BUILD_CONTEXT}}`
- Repository card: `{{CARD_PATH}}`
- Method repository: `{{METHOD_REPOSITORY}}`
- Method commit: `{{METHOD_COMMIT}}`
- Target repository: `{{TARGET_REPOSITORY}}`
- Target workspace: `{{TARGET_WORKSPACE}}`
- Target branch: `{{TARGET_BRANCH}}`
- History range: `{{HISTORY_RANGE}}`
- Delivery policy: `{{DELIVERY_POLICY}}`
- Prepared at: `{{PREPARED_AT}}`

## Execute

1. Verify the method checkout HEAD equals the exact method commit above.
2. Read the method root `SKILL.md`, then read `playbooks/prompts/repository-learning.md` completely. Read the build context, repository card and target repository instructions in the order required there.
3. Confirm this process was launched with `agents.enabled=false`, owns only this repository, and may write only the target repository/worktree plus the repository card directory. Treat the Company Jarvis repo and `CONSTRUCTION-JOURNAL.md` as read-only.
4. Claim the card only when no live or unknown writer exists. Execute every Repository Learning phase and completion gate; do not optimize for a fixed skill count or a generic category-only audit.
5. Deliver through the recorded branch/review policy. Set the card to `delivered-awaiting-coordinator-verification`, not `completed`, and record exact evidence and remote refs.
6. End with exactly this customer action: `Repository Learning 已交付待验收。请回到原 create-jarvis 会话回复：继续。`

If the work pauses, update the card with a re-verifiable checkpoint and `Next`. Resume only this repository with `codex resume`; never continue to a second repository in this chat.
