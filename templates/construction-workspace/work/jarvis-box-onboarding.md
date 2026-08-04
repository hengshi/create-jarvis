# Work card: Jarvis Box installation and onboarding

- Objective: select Native or Docker, install from a verified public release, and prove one supervised runtime happy path
- Completion gate: selected environment passes Runtime Foundation, Agent, provider/writeback and cleanup probes; selected workflow is ready-for-shadow
- Authorized inputs: reconciliation evidence, immutable Company/repo refs, public Jarvis Box release, customer-approved runtime identity and sources
- Allowed writes: approved deployment target, this card, task-local evidence, Company governance factual writeback
- Selected deployment mode: `unresolved`
- Runtime owner: `unresolved`
- Construction Workspace: `unresolved`
- Canonical Company Jarvis checkout: `unresolved`
- Actual runtime root/deployment home: `unresolved`
- Runtime path-separation evidence: `none`
- Target deployment: `unresolved`
- Target workspace: `unresolved`
- Target release/image: `unresolved`
- Connector boundary: `unresolved`
- Writer: `unassigned`
- Provider/session handle: `none`
- Status: `waiting-for-reconciliation`
- Last verified checkpoint: `none`
- Delivered artifacts: `none`
- Evidence: `none`
- Blocker: `waiting for a construction-ready workflow`
- Next: `Verify Reconciliation Gate`
- Last verified: `{{CREATED_AT}}`

## Checkpoints

- [ ] Reconciliation and construction-ready workflow are verified
- [ ] Customer selected Native or Docker
- [ ] Public release and checksum are verified
- [ ] Runtime owner and actual runtime root/deployment home are observed
- [ ] Construction Workspace, Company Jarvis checkout and deployment home are absolute, pairwise disjoint and pass `validate_runtime_paths.py`
- [ ] Native identity reuse or Docker credential import capability is verified without recording secrets
- [ ] Runtime Foundation doctor and real Agent discovery pass
- [ ] Provider or IM ingress → Task/Run → workspace → Agent → writeback → cleanup passes
- [ ] Optional connector and Docker-socket authority are explicitly dispositioned
- [ ] Stable customer runtime facts are reconciled with Company governance
- [ ] Selected workflow is ready-for-shadow
