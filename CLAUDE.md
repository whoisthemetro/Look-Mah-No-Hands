# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository status

This repository is currently empty — no source code, build tooling, or dependencies have been committed yet. The conventions below (notably `npx vue-tsc` for type-checking) indicate this is intended to be a **Vue + TypeScript** project. When the codebase is scaffolded, update this file with the real build/lint/test commands and an architecture overview.

## Plans

Always write implementation plans to `docs/plans/`.

- **Filename format:** `YYYY-MM-DD-NN-SHORT-SLUG.md` — `NN` is a zero-padded sequence number scoped to that day. Pick the next free number by listing the directory.
- This is the canonical location. Do **not** scatter plans into `docs/` root, `ai_context/`, or alongside code.
- Browse existing plans in `docs/plans/` for the expected detail level: goal, why-it-matters, constraints, architecture-fit, phases, verification, open questions.

## Plan execution

When executing a plan (handed to you or pointed at in `docs/plans/`):

1. **Always launch a review agent after the implementation agents finish**, unless the user explicitly says otherwise. The reviewer reads the diff against the plan's acceptance criteria and existing codebase patterns and reports one of: `shippable`, `shippable-with-fixes`, or `not-shippable`.
2. **If the reviewer says `shippable`, ship without further confirmation:** cut a fresh feature branch off `main` (never commit to local `main` directly), verify there (imports, `npx vue-tsc`, smoke tests), push the branch, and open a PR via `gh pr create`. `main` advances only when the PR merges on GitHub. This is pre-authorized by this rule — the usual "confirm before pushing/PRing" default does not apply here.
3. **Exception — sequential multi-plan execution:** don't auto-ship between plans. Accumulate on one branch and ship at the end (one PR per logical-change boundary).
4. **If the reviewer flags fixes:** fix, re-review, then ship. **`not-shippable`:** stop and report — never ship a known-broken thing.
