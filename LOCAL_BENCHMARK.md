# Running MALT Locally

These steps run the MALT green agent against this purple agent with Docker Compose.

## 1. Build Images

From this purple-agent repo:

```bash
cd /data2/gnanesh/ProjectNetArena/malt-purple-agent
docker build --platform linux/amd64 -t malt-purple-agent:local .
```

From the NetArena repo:

```bash
cd /data2/gnanesh/ProjectNetArena/NetArena
docker build --platform linux/amd64 -f app-malt/green_agent/Dockerfile -t malt_agent:local .
```

## 2. Create a Local Scenario

Use the leaderboard repo because it has `generate_compose.py`.

```bash
cd /data2/gnanesh/ProjectNetArena/netarena_leaderboard
cat > malt_local_scenario.toml <<'TOML'
[green_agent]
image = "malt_agent:local"
env = { LOG_LEVEL = "INFO" }

[[participants]]
image = "malt-purple-agent:local"
name = "malt_operator"
[participants.env]
    NEBIUS_API_KEY = "${NEBIUS_API_KEY}"
    NEBIUS_API_BASE = "${NEBIUS_API_BASE}"
    MODEL_NAME = "openai/Qwen/Qwen3-Next-80B-A3B-Thinking"

[config]
prompt_type = "zeroshot_base"
complexity_level = ["level1", "level2", "level3"]
num_queries = 3
output_dir = "dump"
output_file = "query_output.jsonl"
benchmark_path = "assessment_queries.jsonl"
regenerate_query = true
TOML
```

For a quick smoke test, set `num_queries = 1`.

The purple image defaults to no few-shot examples. To test few-shot, generate
the compose files first, then add `--few-shot` to the `malt_operator` service
`command` in `docker-compose.yml`.

## 3. Generate Compose Files

```bash
python3 generate_compose.py --scenario malt_local_scenario.toml --app malt
```

This writes:

- `docker-compose.yml`
- `a2a-scenario.toml`
- `.env.example` with the secrets needed by the scenario
- `output/`

## 4. Add Secrets for Docker Compose

```bash
cp .env.example .env
```

Edit `.env` and fill:

```env
NEBIUS_API_KEY=...
NEBIUS_API_BASE=https://api.studio.nebius.ai/v1
```

## 5. Run the Benchmark

```bash
docker compose up --abort-on-container-exit agentbeats-client
```

The result lands in:

```text
/data2/gnanesh/ProjectNetArena/netarena_leaderboard/output/results.json
```

## 6. Summarize Results

```bash
python3 - <<'PY'
import json
from pathlib import Path

path = Path("output/results.json")
data = json.loads(path.read_text())
rows = data.get("results", [])

def avg(key):
    vals = [row.get(key) for row in rows if isinstance(row.get(key), (int, float))]
    return sum(vals) / len(vals) if vals else None

print("rows:", len(rows))
for key in ("correctness", "safety", "latency"):
    value = avg(key)
    print(f"avg_{key}:", None if value is None else round(value, 4))

for i, row in enumerate(rows, 1):
    if row.get("correctness") != 1 or row.get("safety") != 1:
        print(f"\nfailure row {i}")
        print(json.dumps(row, indent=2)[:4000])
PY
```

## Public Submission Note

For official GitHub Actions leaderboard submissions, use `agentbeats_id` in
`malt_scenario.toml`, not local `image = ...`. Local `image = ...` is only for
Docker testing on this machine.
