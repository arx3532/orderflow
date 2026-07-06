# OrderFlow

A multi-agent AI system for conversational food-delivery and grocery ordering, built with LangGraph and FastAPI. OrderFlow orchestrates separate agent nodes for food ordering and grocery (Instamart-style) ordering behind a single conversational interface, using the Model Context Protocol (MCP) to talk to underlying ordering services.

> **Status:** Actively in development. Core multi-agent architecture and food-ordering flow work end-to-end. Grocery/Instamart agent integration is in progress.

## Why this project exists

Most "AI agent" demos are single-purpose chatbots wrapped around one API. OrderFlow is an exploration of a harder problem: how do you cleanly compose *multiple* independent, stateful agents (food ordering, grocery ordering, and more to come) into one conversational system, without their state, tools, or control flow bleeding into each other?

## Architecture

- **Framework:** LangGraph `StateGraph` + FastAPI
- **LLM:** Mistral Medium 3.5 (128B) via NVIDIA NIM
- **Tool integration:** MCP client wrappers around external ordering services, with each domain (food, grocery) treated as an isolated agent client
- **State management:** Flat `StateGraph` design (see below) with `add_messages` reducer and a checkpointer singleton for persistence across turns

### Flat graph over subgraphs

The initial design nested each domain agent (food, grocery) as its own LangGraph *subgraph*, on the assumption that isolation at the graph level would keep state clean between domains.

In practice, this broke `interrupt`/`resume` flows: when a node inside a subgraph paused for human input (e.g. confirming an address or an order), resuming it did not reliably restore the correct state, because checkpointing and resumption behave differently across subgraph boundaries than LangGraph's docs suggest for single-graph use.

After tracing several silent state-loss bugs back to this, I rebuilt the system around a **single flat `StateGraph`**, where each domain agent is a set of uniquely-named nodes with conditional edges routing between them, rather than a nested graph. This traded some structural encapsulation for correctness and predictability in interrupt/resume behavior — a worthwhile trade for a system where "confirm this order" style human-in-the-loop steps are core to the product, not an edge case.

## Tech stack

- Python, FastAPI
- LangGraph (StateGraph, conditional edges, checkpointer)
- MCP client/server integration
- NVIDIA NIM (Mistral Medium 3.5 128B)

## Roadmap

- [x] Food ordering agent with MCP integration
- [x] Flat StateGraph migration (interrupt/resume fix)
- [ ] Grocery/Instamart agent using `interrupt_before` with dedicated node names in the flat graph
- [ ] Shared cart/session state across domain agents
- [ ] Basic eval suite for multi-turn ordering conversations

## Notes

This is a personal learning project built to go deep on multi-agent orchestration patterns, not a production service. Contributions/issues welcome if you're exploring similar LangGraph architecture questions.
