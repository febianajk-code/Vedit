# Bug log: <project name>

Severity: S1 data loss, crash, or the core loop broken for everyone.
S2 a must-have flow broken for a case. S3 annoying, workaround exists.
S4 polish.

| id | severity | screen / flow | what happens | what should happen | status |
| --- | --- | --- | --- | --- | --- |
| B01 | S2 | S08 / F01 | submitting twice books two slots | second submit rejected | open |

## Rules

- One row per bug, found while testing, fixed before launch if S1 or S2.
- Reproduction steps in the row or a linked file; a bug nobody can reproduce
  is closed, not deferred.
- Fixed rows stay in the log with status `fixed`; the log doubles as the
  regression list.
