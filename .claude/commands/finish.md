---
description: Milestone 8 - write README.md and check that the project starts from scratch
allowed-tools: Bash(rm -rf /tmp/clean-check), Bash(mkdir /tmp/clean-check), Bash(tar:*), Bash(cd /tmp/clean-check:*), Bash(uv sync), Bash(uv run:*), Bash(cp q_table.npy:*), Bash(cmp:*), Bash(grep:*), Bash(wc -l:*), Bash(ls:*), Bash(test:*)
---

Milestone 8 of CLAUDE.md. Do only this milestone.

1. Write `README.md`, in English, at most 80 lines, with these sections and
   only the exact commands that really work:
   - what the project is (two or three sentences);
   - requirements: `uv` (it installs the Python of `.python-version`), and, for
     the agent only, the Ollama app running with the model downloaded by
     `ollama pull qwen3:4b`. No token and no `.env` are needed;
   - setup: `uv sync`;
   - tests: `uv run pytest` (offline: no Ollama, no network), expected result
     `44 passed`;
   - run, in this order, one line each saying what it prints or writes:
     `uv run python src/world.py`, `uv run python src/rover_env.py`,
     `uv run python src/train.py` (trains 1500 episodes with random actions
     and rewrites `q_table.npy`; the result is always the same),
     `uv run python src/experiment.py` (writes
     `results/learning_curves.png`), `uv run python src/tools.py`,
     `uv run python src/model.py` and `uv run python src/main.py` (the agent
     answers four requests with the real LLM; it needs Ollama running and takes
     a few minutes; the answers of the model vary);
   - project layout: a short tree of the files that exist;
   - map and rules in six lines: symbols, heights, the three rewards, the
     states (destination x cells), the 100-step limit;
   - a note: the delivered `q_table.npy` is already trained; the tools and the
     agent only read it and never train.
2. Do not write any other file and do not change anything else.
3. Check that the project starts from scratch, with the README commands, in a
   clean copy. Run each command on its own:
   - `rm -rf /tmp/clean-check` and `mkdir /tmp/clean-check`;
   - copy the project without the environment, caches or personal files:
     `tar --exclude=.venv --exclude=__pycache__ --exclude=.pytest_cache
     --exclude=.env --exclude='debug_*' -cf - . | (cd /tmp/clean-check && tar
     -xf -)`;
   - in `/tmp/clean-check`: `uv sync`, then `uv run pytest`, then
     `cp q_table.npy /tmp/clean-check-q-before.npy`, then the six commands of
     the README run list except `src/main.py`, then
     `cmp q_table.npy /tmp/clean-check-q-before.npy` (the retrained table must
     be identical: `cmp` prints nothing);
   - do NOT run `src/main.py`: the student runs it.
4. In the original project folder run: `wc -l CLAUDE.md` (must be less than
   200), `ls -A` (show the full list), `test ! -e .env && echo "no .env"` and
   `grep -rIlE "hf_[A-Za-z0-9]{10,}|HF_TOKEN|HUGGINGFACEHUB_API_TOKEN" --exclude-dir=.venv --exclude-dir=.git --exclude-dir=.claude .`.

Acceptance criteria (show the full output of every command):

- in the clean copy, `uv sync` ends without error and `uv run pytest` ends with
  `44 passed`;
- every README command runs from the clean copy and prints what the README
  says; the retrained `q_table.npy` is identical (`cmp` prints nothing);
- `CLAUDE.md` has less than 200 lines; there is no `.env`; the `grep` prints
  nothing.

Report: the file written, the full output, any command of the README that did
not work (with the fix, as a diff), and the lines the student must review (the
setup, test and run sections of the README).
