-- Software House — Supabase schema
-- All tables referenced across the 21 agent definitions.
-- Designed for append-mostly workloads with version history preserved.

-- =====================================================
-- GOVERNANCE & ORCHESTRATION
-- =====================================================

create table if not exists builds (
  build_id uuid primary key default gen_random_uuid(),
  name text not null,                      -- e.g., "Fade Bot v2", "XCE Reply Enhancement"
  status text not null default 'active',   -- active | complete | cancelled
  prd_url text,
  sdd_url text,
  jsx_refs jsonb,                          -- array of JSX file paths/URLs
  target_repo text,                        -- github URL
  target_branch text default 'main',
  started_at timestamptz default now(),
  completed_at timestamptz,
  post_mortem_id uuid                      -- references skills_library
);
create index on builds (status, started_at desc);

create table if not exists tickets (
  ticket_id text primary key,              -- human-readable e.g., "T-042"
  build_id uuid references builds(build_id),
  title text not null,
  description text,
  acceptance_criteria text,
  owner_desk text not null,                -- backend | frontend | mobile | etc.
  owner_agent text,                        -- specific agent id once assigned
  priority int default 3,
  dependencies text[],                     -- array of ticket_ids this blocks on
  status text not null default 'open',     -- open | planning | in-progress | in-review | in-qa | done | blocked
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  completed_at timestamptz
);
create index on tickets (build_id, status);
create index on tickets (owner_desk, status);

create table if not exists plans (
  plan_id uuid primary key default gen_random_uuid(),
  ticket_id text references tickets(ticket_id),
  author_agent text not null,              -- senior agent that wrote the plan
  executor_agent text,                     -- agent expected to execute
  plan_type text,                          -- backend | frontend | mobile | devops | pinescript | data | qa | backtest
  content jsonb,                           -- structured plan body
  markdown text,                           -- human-readable plan text
  status text default 'active',            -- active | superseded | cancelled
  created_at timestamptz default now()
);
create index on plans (ticket_id);

create table if not exists sprint_log (
  entry_id uuid primary key default gen_random_uuid(),
  build_id uuid references builds(build_id),
  event_type text,                         -- sprint-start | assignment | escalation | unblock | completion | post-mortem
  desk text,
  agent_id text,
  message text,
  metadata jsonb,
  timestamp timestamptz default now()
);
create index on sprint_log (build_id, timestamp desc);

-- =====================================================
-- HERMES SKILLS LIBRARY (self-learning loop)
-- =====================================================

create table if not exists skills_library (
  skill_id uuid primary key default gen_random_uuid(),
  agent_id text not null,                  -- which agent authored this skill
  category text,                           -- pattern | runbook | failure-mode | recipe | experiment
  domain text,                             -- backend | frontend | pinescript | devops | data | backtest | etc.
  title text not null,
  description text,
  when_to_use text,
  content text,                            -- full markdown body
  code_refs jsonb,                         -- pointers to canonical implementations
  tags text[],
  success_count int default 0,
  failure_count int default 0,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
create index on skills_library (domain, category);
create index on skills_library using gin (tags);

-- =====================================================
-- CODE REVIEWS & PR TRACKING
-- =====================================================

create table if not exists code_reviews (
  review_id uuid primary key default gen_random_uuid(),
  ticket_id text references tickets(ticket_id),
  pr_url text,
  reviewer_agent text not null,
  author_agent text,
  verdict text,                            -- approve | request-changes | reject
  plan_id uuid references plans(plan_id),  -- plan the review was against
  comments jsonb,                          -- array of comment objects
  prd_clauses_cited text[],                -- for QA reviews
  created_at timestamptz default now()
);
create index on code_reviews (ticket_id);

-- =====================================================
-- QA & TESTING
-- =====================================================

create table if not exists test_runs (
  run_id uuid primary key default gen_random_uuid(),
  ticket_id text references tickets(ticket_id),
  test_type text,                          -- unit | integration | e2e | functional | indicator | regression
  runner_agent text not null,
  platform text,                           -- web | ios | android | tradingview | quantower | api
  status text,                             -- pass | fail | flaky | error
  passed int default 0,
  failed int default 0,
  skipped int default 0,
  duration_seconds numeric,
  evidence jsonb,                          -- screenshots, traces, network logs
  summary text,
  created_at timestamptz default now()
);
create index on test_runs (ticket_id, created_at desc);
create index on test_runs (runner_agent, status);

create table if not exists incidents (
  incident_id uuid primary key default gen_random_uuid(),
  ticket_id text references tickets(ticket_id),
  severity text,                           -- critical | high | medium | low
  category text,                           -- bug | flaky-test | silent-failure | infra | spec-drift
  reporter_agent text not null,
  title text not null,
  expected text,
  actual text,
  reproduction text,
  root_cause_suspicion text,
  evidence jsonb,
  status text default 'open',              -- open | in-progress | resolved | wont-fix
  resolved_at timestamptz,
  created_at timestamptz default now()
);
create index on incidents (status, severity);

-- =====================================================
-- DESIGN SYSTEM
-- =====================================================

create table if not exists design_system (
  entry_id uuid primary key default gen_random_uuid(),
  entry_type text,                         -- token | component | pattern | asset
  platform text,                           -- web | ios | android | cross-platform
  name text not null,
  description text,
  figma_url text,
  asset_paths jsonb,                       -- for images/icons
  code_ref text,                           -- repo path to canonical implementation
  usage_notes text,
  created_by text,                         -- agent id
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
create index on design_system (entry_type, platform);

-- =====================================================
-- INFRASTRUCTURE
-- =====================================================

create table if not exists infra_config (
  config_id uuid primary key default gen_random_uuid(),
  environment text not null,               -- staging | production | sandbox
  service text not null,
  platform text,                           -- aws | railway | vercel | supabase | hyperliquid-node
  region text,
  config jsonb,
  terraform_state_ref text,
  last_applied_at timestamptz,
  applied_by text,
  notes text,
  created_at timestamptz default now()
);
create index on infra_config (environment, service);

-- =====================================================
-- PINESCRIPT / INDICATORS
-- =====================================================

create table if not exists indicator_specs (
  spec_id uuid primary key default gen_random_uuid(),
  ticket_id text references tickets(ticket_id),
  name text not null,
  version text,
  target_platform text,                    -- tradingview-v5 | tradingview-v6 | quantower
  hypothesis text,
  entry_rules text,
  exit_rules text,
  parameters jsonb,                        -- array of {name, default, min, max, description}
  alert_conditions text,
  plots text,
  target_assets text[],
  target_timeframes text[],
  status text default 'draft',             -- draft | approved | implemented | tested | shipped
  created_at timestamptz default now()
);
create index on indicator_specs (status);

-- =====================================================
-- DATA & BACKTESTING
-- =====================================================

create table if not exists datasets (
  dataset_id uuid primary key default gen_random_uuid(),
  name text not null,
  source text,                             -- binance | bybit | hyperliquid | tradingview-export | ccxt-multi
  asset text,
  timeframe text,
  date_range daterange,
  row_count bigint,
  file_path text,
  provenance jsonb,                        -- source details, cleaning steps, known limitations
  audit_status text,                       -- pending | passed | failed | conditional
  created_at timestamptz default now()
);
create index on datasets (asset, timeframe);
create index on datasets (audit_status);

create table if not exists data_audits (
  audit_id uuid primary key default gen_random_uuid(),
  dataset_id uuid references datasets(dataset_id),
  auditor_agent text not null,
  checks_run jsonb,                        -- array of {check_name, passed, details}
  verdict text,                            -- passed | failed | conditional
  flags text[],                            -- gap | survivorship | look-ahead | timezone-drift | etc.
  notes text,
  created_at timestamptz default now()
);
create index on data_audits (dataset_id);

create table if not exists experiments (
  experiment_id uuid primary key default gen_random_uuid(),
  ticket_id text references tickets(ticket_id),
  hypothesis text not null,
  baseline_params jsonb,
  parameter_grid jsonb,
  metric_list text[],
  acceptance_criteria text,
  multiple_testing_correction text,
  stopping_rule text,
  dataset_ids uuid[],
  indicator_spec_id uuid references indicator_specs(spec_id),
  status text default 'designed',          -- designed | running | complete | abandoned
  verdict text,                            -- green | yellow | red | inconclusive
  created_at timestamptz default now()
);
create index on experiments (status);

create table if not exists backtest_results (
  result_id uuid primary key default gen_random_uuid(),
  experiment_id uuid references experiments(experiment_id),
  parameter_set jsonb,                     -- exact params for this run
  dataset_id uuid references datasets(dataset_id),
  asset text,
  timeframe text,
  window text,                             -- in-sample | out-of-sample | walk-forward-{N}
  sharpe numeric,
  sortino numeric,
  max_drawdown numeric,
  hit_rate numeric,
  profit_factor numeric,
  trade_count int,
  avg_trade_duration_minutes numeric,
  total_return numeric,
  equity_curve_path text,
  raw_metrics jsonb,
  run_at timestamptz default now()
);
create index on backtest_results (experiment_id, sharpe desc);
