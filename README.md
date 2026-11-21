# Store Coach — Manyavar (VCH3)

Live app: https://santos1995.github.io/vch3-store-coach/

Built from scratch at Vibe Coders Hackathon Edition 3 (Kolkata, 21 Nov 2026) for case study A: Store Coach, Vedant Fashions Limited.

## What it does
Every morning, without anyone asking:
- Each area manager sees which of their stores need attention and why, ranked by rupees at stake (max 5 issues), each with the lever, the cause and one action that names who, what and when.
- Each salesperson gets one card: one behaviour, a peer from their own store, one action for today (60 words or fewer).

Three levers: conversion (bills / footfall), items per bill, return customers (30+ days). Comparisons are fair: a salesperson is compared with peers in their own store, city and state.

Festival and wedding days are shown as context, not alerts. Numbers that cannot be right are flagged as data issues, not alerts.

## Data
Snapshot date: 31 Oct 2026 (the pack's "today"). The hackathon pack's data is synthetic; no real store, salesperson or customer is in it. This repo contains only small derived aggregates (data.js). Raw CSVs are excluded by .gitignore and never committed. Data and briefs belong to Vedant Fashions Limited.

## How it works
- `aggregate.py` (run once, locally) reads the pack CSVs and writes the aggregates in `data.js`.
- `index.html` is a static app (GitHub Pages) that renders the morning brief and store drill-down from those aggregates. Scores, rankings and actions are deterministic rule-based logic.
- Optional: a one-paragraph manager note can be drafted by Sarvam AI through a small proxy. The badge shows honestly whether the note is AI-written or the local fallback. Rankings and actions never depend on the AI.
