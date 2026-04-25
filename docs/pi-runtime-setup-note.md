# Pi Runtime Setup Note

## Purpose

This note records the currently validated local Pi runtime setup for DaoShuGuo.

## Validated Environment

- Node: `v22.22.0`
- npm: `11.7.0`
- pnpm: `10.31.0`

## Local Feasibility Root

Validated in:

```text
/tmp/daoshuguo-pi-feasibility
```

Contents:

- `pi-mono`
- `pi-autoresearch`
- isolated `home/`

## Build Steps

Clone:

```bash
git clone https://github.com/badlogic/pi-mono.git /tmp/daoshuguo-pi-feasibility/pi-mono
git clone https://github.com/davebcn87/pi-autoresearch.git /tmp/daoshuguo-pi-feasibility/pi-autoresearch
```

Install:

```bash
cd /tmp/daoshuguo-pi-feasibility/pi-mono
npm install
```

Build:

```bash
npm run build
```

## Known Constraint

Pi build may require execution outside the stricter sandbox because `tsx` can create IPC pipes under `/tmp`.

## Isolated HOME

Use an isolated HOME instead of polluting the real user home:

```bash
HOME=/tmp/daoshuguo-pi-feasibility/home
```

This allows Pi to create:

- `~/.pi/agent/settings.json`
- `~/.pi/agent/auth.json`
- session directories

## CLI Smoke Checks

```bash
HOME=/tmp/daoshuguo-pi-feasibility/home \
node /tmp/daoshuguo-pi-feasibility/pi-mono/packages/coding-agent/dist/cli.js --version

HOME=/tmp/daoshuguo-pi-feasibility/home \
node /tmp/daoshuguo-pi-feasibility/pi-mono/packages/coding-agent/dist/cli.js --help
```

## Package Discovery Check

```bash
HOME=/tmp/daoshuguo-pi-feasibility/home \
node /tmp/daoshuguo-pi-feasibility/pi-mono/packages/coding-agent/dist/cli.js list
```

## Current Validated Packages

- `pi-autoresearch`
- `daoshuguo-research-loop`

## Current Limitation

The validated surface is:

- build
- install
- package discovery
- JSON mode startup

Not yet validated:

- full authenticated provider workflow
- Pi RPC orchestration
- long-running autonomous DaoShuGuo loop
