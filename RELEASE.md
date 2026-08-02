# Release model

`create-jarvis` is the customer-construction method. It is not Jarvis Box and does not share the Jarvis Box runtime version.

## Repository relationship

| Repository | Responsibility |
| --- | --- |
| `github.com/hengshi/create-jarvis` | Versioned construction, recovery, reconciliation, and runtime-onboarding method consumed by an authenticated Host Agent |
| `gitlab.hengshi.org/henglabs/jarvis-box` | Canonical private Jarvis Box source, tests, CI, image build, and release artifacts |
| `github.com/hengshi/jarvis-box` | Curated public Jarvis Box documentation and verified runtime Releases |
| Customer Company Jarvis | Customer-owned knowledge, workflow, governance, and skills |

`create-jarvis` consumes only a published `github.com/hengshi/jarvis-box` Release during runtime onboarding. It never consumes the private GitLab source or copies Jarvis Box internals into the customer repository.

## Version contract

- `create-jarvis vA.B.C` versions the construction method.
- `jarvis-box vX.Y.Z` versions the runtime.
- A Construction Workspace records the exact create-jarvis tag and commit.
- The onboarding card records the independently selected Jarvis Box tag, artifact checksum, and production image digest.
- `main` is development state and is never a stable customer input.

## Release flow

1. Merge a pull request whose `test / behavior` check passes.
2. Move the completed changelog entries from `Unreleased` to the target version.
3. Create and push an annotated semantic-version tag on the tested `main` commit:

```bash
version=X.Y.Z
git tag -a "v$version" -m "create-jarvis v$version"
git push origin "v$version"
```

4. The tag workflow reruns the complete behavior suite, validates the tag against this changelog, and creates the GitHub Release.
5. The release is complete only when the GitHub Release exists. A tag without a Release is not a stable method version.

The first stable method release is `v0.1.0`. Later method releases do not require a Jarvis Box release unless the method actually depends on a new public runtime contract.
