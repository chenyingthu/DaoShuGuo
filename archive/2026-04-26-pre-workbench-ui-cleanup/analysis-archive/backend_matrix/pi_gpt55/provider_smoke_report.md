# Pi-Agent GPT-5.5 Provider Smoke Report

## Configuration

Source Codex config:

- file: `/home/chenying/.codex/config.toml`
- provider: `codex`
- model: `gpt-5.5`
- base URL: `https://relay.nf.video/v1`
- wire API: `responses`

Pi mapping:

- file: `/home/chenying/.pi/agent/models.json`
- provider: `codex-relay`
- model: `gpt-5.5`
- API: `openai-responses`
- API key source: dynamic shell read from `/home/chenying/.codex/auth.json`

Pi defaults:

- file: `/home/chenying/.pi/agent/settings.json`
- defaultProvider: `codex-relay`
- defaultModel: `gpt-5.5`

Backups were created with timestamp:

`20260425T153715Z`

## Tests

### Model Discovery

Command:

```bash
pi --list-models gpt-5.5 --offline
```

Observed:

```text
provider     model    context  max-out  thinking  images
codex-relay  gpt-5.5  1M       16.4K    yes       no
```

### Text-Only Smoke

Command:

```bash
pi --provider codex-relay --model gpt-5.5 --thinking off --no-session --no-tools -p "Reply with exactly: PI_GPT55_OK"
```

Observed:

```text
PI_GPT55_OK
```

### Tool-Calling Smoke

Command:

```bash
pi --provider codex-relay --model gpt-5.5 --thinking off --no-session --mode json --tools ls -p "Use the ls tool on the current directory, then reply with exactly PI_GPT55_TOOL_OK and one filename you saw."
```

Artifact:

`analysis/backend_matrix/pi_gpt55/text_and_ls_tool_smoke.jsonl`

Observed final answer:

```text
PI_GPT55_TOOL_OK README.md
```

Observed tool events:

- `tool_execution_start`
- `tool_execution_end`
- final `agent_end`

## Conclusion

Pi-agent can use the same GPT-5.5 relay model family as the current Codex configuration through a custom `codex-relay` provider.

The minimal tests prove:

- provider/model discovery works
- authentication works
- text-only generation works
- at least one built-in tool call works through `openai-responses`

This does not yet prove full DaoShuGuo research-loop compatibility. The next required step is a bounded Pi GPT-5.5 loop smoke using DaoShuGuo tools and required loop artifacts.
