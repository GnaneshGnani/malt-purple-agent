# MALT Purple Agent

AgentBeats-compatible purple agent for the NetArena MALT data-center planning benchmark.

This repo uses the **no-helper safety prompt** for the public submission. The running agent does not mention or call benchmark helper functions such as `solid_step_*`; it asks the model to generate ordinary NetworkX code and applies a lightweight output guard before returning the response.

The helper-aware experiment is preserved separately in [`helper_prompts.py`](helper_prompts.py) for later reference. That file is intentionally not imported by the runtime and is excluded from the Docker build context.

## Layout

| File | Role |
|------|------|
| [`server.py`](server.py) | A2A HTTP server entrypoint |
| [`cli.py`](cli.py) | CLI args and default model selection |
| [`prompts.py`](prompts.py) | Active no-helper MALT prompt and optional few-shot examples |
| [`helper_prompts.py`](helper_prompts.py) | Archived helper-aware prompt, not used at runtime |
| [`output.py`](output.py) | Lightweight MALT output guard |
| [`litellm_backend.py`](litellm_backend.py) | LiteLLM call path, prompt assembly, one retry on invalid output |
| [`executor.py`](executor.py) | A2A executor wrapper |
| [`LOCAL_BENCHMARK.md`](LOCAL_BENCHMARK.md) | Local Docker benchmark recipe |

## Active MALT Behavior

The active MALT prompt asks the model to:

- Return one Python fenced block containing `def process_graph(graph_data)`.
- Use `copy.deepcopy(graph_data)` and normal NetworkX traversal.
- Return exactly `{"type": ..., "data": ..., "updated_graph": ...}`.
- Use node attributes like `attrs["name"]` for lookup.
- Create `EK_PORT` nodes with `physical_capacity_bps=1000`.
- Create `EK_PACKET_SWITCH` nodes with at least one child `EK_PORT`.
- Keep `updated_graph` safe for mutation-then-text/list/count/rank tasks unless the user explicitly asks for a graph.

The active prompt and optional few-shot examples are in [`prompts.py`](prompts.py). They do not contain `solid_step_*` helper calls.

MALT is treated as one-shot: the agent does not keep or replay conversation history across requests. Few-shot examples are disabled by default. Pass `--few-shot`, or set `MALT_FEW_SHOT=1`, to prepend the static examples to each request.

The output guard checks only response shape and obvious unsafe/invalid code:

- Python fenced block exists.
- `def process_graph(graph_data)` exists.
- Python syntax parses.
- `updated_graph` appears.
- No imports, `print`, dynamic execution, or `solid_step_*` helper calls.

It does **not** copy the green verifier or ground-truth logic.

## Local Server

Create a local env file:

```bash
cp .env.example .env
```

Fill in one provider block, for example:

```env
NEBIUS_API_KEY=...
NEBIUS_API_BASE=https://api.studio.nebius.ai/v1
MODEL_NAME=openai/Qwen/Qwen3-Next-80B-A3B-Thinking
```

Run locally:

```bash
python3 server.py --host 0.0.0.0 --port 9009 --card-url http://localhost:9009
curl -sf http://localhost:9009/.well-known/agent-card.json
```

Enable the static examples explicitly:

```bash
python3 server.py --host 0.0.0.0 --port 9009 --card-url http://localhost:9009 --few-shot
```

## Docker

```bash
docker build --platform linux/amd64 -t malt-purple-agent:local .
docker run --rm -p 9009:9009 \
  -e NEBIUS_API_KEY="$NEBIUS_API_KEY" \
  -e NEBIUS_API_BASE="${NEBIUS_API_BASE:-https://api.studio.nebius.ai/v1}" \
  -e MODEL_NAME="openai/Qwen/Qwen3-Next-80B-A3B-Thinking" \
  malt-purple-agent:local \
  --host 0.0.0.0 --port 9009 --card-url http://localhost:9009
```

For few-shot Docker runs, append `--few-shot` to the container command or set `MALT_FEW_SHOT=1`.

## Local Benchmark

Use [`LOCAL_BENCHMARK.md`](LOCAL_BENCHMARK.md) for the full Docker Compose flow against the MALT green agent.

## AgentBeats Registration

Register this as a purple agent using:

```text
Name: MALT Purple Agent
Hosted method: Docker Image
Docker image URL: ghcr.io/gnaneshgnani/malt-purple-agent:v1
Repository link: https://github.com/GnaneshGnani/malt-purple-agent
```

If the AgentBeats form asks for an Amber manifest URL, use:

```text
https://raw.githubusercontent.com/GnaneshGnani/malt-purple-agent/main/amber-manifest.json5
```

For official leaderboard runs, the scenario file must use the registered `agentbeats_id`. Local `image = ...` scenarios are only for machine-local testing.
