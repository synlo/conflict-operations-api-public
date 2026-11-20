# Brain: project memory with evidence

Brain is the planned persistent engineering memory for AddonRelay's framework workflows. It should help an agent or developer recover the project's state, find relevant previous failures and decide what observation would settle the next question.

**Public Brain integration is planned.** Existing local reports and optional history are useful, but they are not yet the complete evidence-aware project memory described here. See [Capabilities](CAPABILITIES.md) for what is available and [Start here](START_HERE.md) for current tools.

## What Brain should do

An agent session can end while a developer is investigating a resource problem or waiting for a native check. The next session should be able to answer:

- What operation actually completed, and where is its evidence?
- What failed, and was that a product defect, setup problem or invalid observation?
- Which correction was attempted, and what changed?
- Which previous results still apply to these inputs?
- What remains unobserved, and what is the next useful check?

Brain retains the information needed to answer those questions. It does not replace the controller, operation journal or original receipts. Memory is a way to retrieve and explain evidence; it cannot issue permissions or manufacture a successful result.

## Three knowledge scopes

| Scope | Intended contents | Intended access |
|---|---|---|
| Project memory | One project's failures, hypotheses, corrections, observations and continuation | Local to that selected project by default |
| Team memory | Project knowledge deliberately shared by its owner | Named collaborators when team support is implemented |
| Reviewed references | Original or redistribution-cleared examples, lessons and source references | A versioned reference collection, separate from private project evidence |

These scopes should remain visibly distinct in search results. A useful shared lesson may come from another project, but that project's test cannot count as a local test. Team sharing must not silently publish a lesson to every user.

Private customer material and the project's own internal development history are not a starter corpus. Shared references require their own review, rights and publication process. Users should be able to benefit from a reviewed collection without contributing their private source or logs.

## What a lesson records

The planned lesson format should preserve:

- A stable identity, knowledge scope and actual observation time.
- The error signature or engineering question.
- The observed owner or an explicit unknown classification.
- Relevant project, engine, provider, source and test identities.
- The attempted correction and its changed inputs.
- Failed hypotheses as well as successful scoped outcomes.
- Evidence references and the limits of each conclusion.
- Any successor that corrects an earlier interpretation.

Corrections should append a new assessment rather than erase the original failure. Replaying an imported event must not increase its occurrence count or make old evidence look recent. A retried indexing operation must not become a second engineering event.

For example, a synthetic tutorial might show a resource reference that cannot be resolved. A developer changes the reference and then completes a native compile. The lesson should preserve both the original failure and the successful compile, including the actual inputs. It must not add a claim about the resource's rendered appearance unless that appearance was observed separately.

## Relevant advice is different from reusable proof

Search should prefer an exact applicable error before related failure families. Each returned lesson should explain what matches, what differs and why it is being shown.

| Result type | Appropriate use |
|---|---|
| Exact previous local result with matching relevant identities | Consider reusing the specific observation under the framework's evidence rules |
| Similar failure with changed engine, provider or source inputs | Use it to form a hypothesis and select a focused check |
| Reviewed example from another project | Learn a technique; establish local behavior independently |
| Historical or incomplete result | Understand what happened and what remains unresolved |

Unknown identities remain unknown. Similar wording, a matching filename or a familiar error does not prove that a correction applies. The interface should display the limits next to the result, rather than burying them in a separate disclaimer.

The first useful implementation can use deterministic signature lookup and text search. A vector database, hosted language model or training pipeline is not necessary to record and retrieve project lessons. If such features are considered later, they require their own value, privacy and quality evaluation.

## Recovery and memory have different responsibilities

The operation journal determines whether work was admitted, started, stopped or completed. Original receipts retain the observations. Brain retrieves the relevant parts and helps explain the next action.

If the agent disconnects during a compile, recovery first checks the owned process and durable records. It does not ask a remembered suggestion to decide whether the compile ran. If the native result is sealed but memory indexing fails, the compile result remains valid at its recorded scope. The import can be retried using the same event identity.

Likewise, a remembered workaround cannot extend a deadline, increase an allowance, bypass a prerequisite or supply executable instructions. A lesson can recommend a reviewed recipe; the controller still prepares and validates that operation.

## Privacy and control

Project memory should be local by default, with clear inspection, export and deletion controls. Exporting a support report, sharing with a team and contributing a public lesson are different actions. None should imply the others.

Before sharing, show the exact selected material and its destination. Review it for credentials, player data, private paths, proprietary source and sensitive metadata. A hash or identifier may still reveal information about a project, so sanitized output should not automatically be described as anonymous.

An AI agent may receive selected memory results through its configured client. That provider's processing is a separate data path from local storage. The product should explain this when connecting a client and when preparing an export. See [Privacy](PRIVACY.md).

The proposed Brain does not imply automatic model training on customer data. Optional hosted analysis and later team features must state their own submitted fields, purpose, access and retention. They should not require access to an operator's private knowledge service or credentials.

## How the first public milestone will be demonstrated

The first memory demonstration should use an unrelated owned sample project:

1. Observe a real, bounded failure through the supported native route.
2. Correct its cause and record the changed input.
3. Complete the affected check and retain its scoped evidence.
4. End the agent session and reconnect.
5. Recover the result without rerunning the engine merely to reconstruct context.
6. Retrieve the lesson with its source, applicability and remaining limits.
7. Show that another project cannot claim this project's result as its own proof.

That demonstrates useful continuity and evidence handling. It does not establish every later memory, team or hosted feature. The [roadmap](ROADMAP.md) separates these acceptance scopes, while the [architecture](ARCHITECTURE.md) explains how memory connects to the shared execution system.
