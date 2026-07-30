# Construction Workspace

This directory is the durable coordination and recovery surface for one customer Jarvis journey. Continue from `CONTINUE-JARVIS.md`; do not initialize a second workspace for the same journey.

The pinned create-jarvis checkout owns the templates and scripts. Use its `scripts/instantiate_construction_workspace.py add-repository` command to add one independent card for each explicitly authorized code repository.

The workspace contains coordination and recovery facts only. Do not store customer source bodies, credentials or jarvis-box runtime state here.
