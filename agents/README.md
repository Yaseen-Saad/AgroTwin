# AgroTwin — Two-Agent Build Room

This folder is the live coordination surface for the two-agent sprint. It is **not** the product
spec. `SPEC.md` defines what we build, `AGENTS.md` defines the engineering rules, and this folder
defines who does what, in which order, and how we talk.

> Sprint: NASA Space Apps 2026 · Gate 0 → Submit · Cairo time
> Lead: **Agent L** (team leader, merge owner)
> Builder: **Agent B** (implementation owner)

---

## 1. The two agents

| Agent | Role | Owns (write) | Reads | Never edits |
| --- | --- | --- | --- | --- |
| **L** | Lead, integrator, release owner | `SPEC.md`, `AGENTS.md`, `HANDOFF.md`, `contracts/`, `VERSION`, `pyproject.toml`, `Makefile`, `tasks.ps1`, `api/`, `web/`, `content/`, `council/`, `qa/`, `docs/`, `agents/TASKS.md`, `agents/STATUS.md` | everything | `ingest/`, `engine/`, `data/`, `scout/` without a task |
| **B** | Builder, computational core | `ingest/`, `engine/`, `data/cache/`, `data/prices.csv`, `scout/`, `tests/ingest/`, `tests/engine/`, `tests/econ/`, `tests/fusion/`, `tests/scout/` | contracts, fixtures, docs | contracts, `api/`, `web/`, `content/`, `council/`, `qa/`, `docs/`, `agents/TASKS.md` |

During this sprint Agent L absorbs the old roster roles **0, 5, 6, 7, 8, 10**. Agent B absorbs
roles **1, 2, 3, 4, 9**. The full role descriptions remain in `AGENTS.md` §16 and the planning
document; this split only changes who executes them.

---

## 2. The loop

We run a strict, short loop. One task in progress per agent.

```text
Lead:   pick task -> write card in TASKS.md -> assignment message in MESSAGES.md
Builder: claim -> implement -> run acceptance -> evidence message in MESSAGES.md
Lead:   review -> run acceptance yourself -> DONE or CHANGES_REQUESTED -> merge
```

1. **Assign.** Lead writes or updates the task card in `TASKS.md`, sets status `ASSIGNED`, and
   appends a message in `MESSAGES.md` with the task id, exact paths, acceptance command and due
   checkpoint.
2. **Claim.** Builder changes the status to `IN_PROGRESS` only by posting a message; the Lead
   updates the board so there is one board owner. Builder states the branch/worktree and the
   first file it will touch.
3. **Execute.** Builder works only in owned paths. If it needs a contract or another folder, it
   posts a `CHANGE_REQUEST` message instead of editing.
4. **Evidence.** Builder runs the acceptance command and appends the command plus the relevant
   output to `MESSAGES.md`. Screenshots are not evidence; commands are.
5. **Review.** Lead re-runs the acceptance on the shared tree. Lead sets `DONE` or
   `CHANGES_REQUESTED` with a precise diff request. Only the Lead merges.
6. **Next.** Lead assigns the next task. If capacity allows, the Builder may self-start the next
   task in its wave immediately after posting evidence; the Lead reviews in parallel.

**WIP limit.** One `IN_PROGRESS` task per agent. Two `REVIEW` tasks maximum. If a task is blocked,
it stays `BLOCKED` and the Builder starts a non-overlapping task from its queue.

---

## 3. Contact protocol

`MESSAGES.md` is the single append-only contact log. Do not use chat history as a source of
truth; if it is not in `MESSAGES.md`, it did not happen.

Every message starts with a header line:

```markdown
### MSG-0007 · Lead → Builder · 2026-11-14 12:30 Cairo · B-02 · IN_PROGRESS
```

Then four short fields:

```text
Task:      B-02
Status:    ASSIGNED | IN_PROGRESS | BLOCKED | REVIEW | CHANGES_REQUESTED | DONE
Body:      one or two sentences, facts only
Evidence:  exact command and result (or "none yet")
Needed by: next checkpoint or "no deadline"
```

Rules:

- Append new messages at the **end** of `MESSAGES.md`; never rewrite old messages.
- Prefix a blocking message with `BLOCKED` in the body and state the exact error and the workaround
  in use.
- A cross-folder request is a message, not an edit. Use the `CHANGE_REQUEST` template below.
- Do not claim a task is done without the acceptance command.
- If the Builder is blocked for 30 minutes, it posts `BLOCKED` and moves on with a mock or the
  next task. The Lead reassigns or cuts.
- The Lead posts a `STATUS` message at every gate and updates `STATUS.md` after every merge.

### Change request template

```text
CHANGE_REQUEST
Need:      <one sentence>
Why:       <contract or demo reason>
Requested: <exact field, file or diff>
Fallback:  <what the Builder is doing meanwhile>
```

---

## 4. Status vocabulary

| Status | Meaning | Who sets it |
| --- | --- | --- |
| `TODO` | Not started, not assigned | Lead |
| `ASSIGNED` | Lead has assigned it | Lead |
| `IN_PROGRESS` | Builder is working | Builder (message), Lead (board) |
| `BLOCKED` | Waiting on a decision, credential or data | Builder (message) |
| `REVIEW` | Evidence posted, waiting for Lead | Builder |
| `CHANGES_REQUESTED` | Lead reviewed; exact changes listed | Lead |
| `DONE` | Lead re-ran acceptance and merged | Lead |
| `CUT` | Removed from scope by the cut order | Lead |

---

## 5. Review and merge discipline

The Lead is the only merge owner. A merge happens only when:

1. The task acceptance command passes on the Lead's machine.
2. `python -m contracts.validate --all` passes.
3. `python -m pytest` passes.
4. `python -m ruff check .` passes.
5. The task is listed as `DONE` in `TASKS.md` and the evidence message exists.
6. `HANDOFF.md` has a gate checkpoint entry.

If `main` is red for 20 minutes, all new work stops until it is green. The Builder does not
commit or push; the Lead commits small, conventional commits.

---

## 6. Honesty rules that never bend

- Contracts are frozen; only the Lead changes them, with a version bump and a fixture.
- Every number carries a source tag. No invented coefficients, prices or citations.
- Modes `LIVE`, `REPLAY`, `SIMULATED`, `NONE` travel with the data and are always visible.
- A mocked result says it is mocked.
- AI use is logged in `docs/AI_USE.md` and in the code/data headers.
- No NASA logos, flags or mission insignia.
- A report without a command is not done.

---

## 7. Fast lane

We are time-boxed. After posting evidence for a task, the Builder may immediately claim the next
task in the same wave if:

- the acceptance command passed locally,
- the next task has no dependency on an unanswered `CHANGE_REQUEST`,
- the paths do not overlap the Lead's active task.

The Lead reviews both tasks in the next checkpoint. This is the only exception to "wait for
review".

---

## 8. Files in this folder

| File | Purpose | Owner |
| --- | --- | --- |
| `README.md` | This protocol | Lead |
| `CHARTER.md` | Mission, roles and decision rights | Lead |
| `TASKS.md` | Live task board, waves and acceptance tests | Lead |
| `MESSAGES.md` | Append-only contact log | Both (append only) |
| `STATUS.md` | Current snapshot: gate, WIP, blockers, last green | Lead |
| `DECISIONS.md` | Architecture and coordination decisions | Lead |
| `prompts/builder-bootstrap.md` | Paste-ready prompt for the Builder session | Lead |
