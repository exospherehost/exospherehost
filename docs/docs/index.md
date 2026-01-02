<p align="center">
<img src="assets/logo-with-bg.png" alt="exosphere logo" style="max-width: 50%;">
</p>

<p align="center">
  <a href="https://docs.exosphere.host"><img src="https://img.shields.io/badge/docs-latest-success" alt="Docs"></a>
  <a href="https://github.com/exospherehost/exospherehost/commits/main"><img src="https://img.shields.io/github/last-commit/exospherehost/exospherehost" alt="Last commit"></a>
  <a href="https://pypi.org/project/exospherehost/"><img src="https://img.shields.io/pypi/v/exospherehost" alt="PyPI - Version"></a>
  <a href="https://codecov.io/gh/exospherehost/exospherehost"><img src="https://img.shields.io/codecov/c/gh/exospherehost/exospherehost" alt="Coverage"></a>
  <a href="https://github.com/orgs/exospherehost/packages?repo_name=exospherehost"><img src="https://img.shields.io/badge/Kubernetes-native-326ce5?logo=kubernetes&logoColor=white" alt="Kubernetes"></a>
  <a href="https://discord.com/invite/zT92CAgvkj"><img src="https://badgen.net/discord/members/zT92CAgvkj" alt="Discord"></a>
  <a href="https://github.com/exospherehost/exospherehost"><img src="https://img.shields.io/github/stars/exospherehost/exospherehost?style=social" alt="Stars"></a>
</p>


# Exosphere: Reliablity runtime for AI agents

**Exosphere** is a lightweight runtime to make AI agents resilient to failure and infinite scaling across distributed compute. With a few changes to your existing agent code, take your agent from demo to deployment.

## Why Exosphere?

Exosphere provides a powerful foundation for building and orchestrating AI applications with these key capabilities:

<div class="feature-grid" markdown>

<div class="feature-card" markdown>

### [Lightweight Runtime](./exosphere/architecture.md)

Execute workflows reliably with minimal overhead across distributed infrastructure using a state-based execution model.

</div>

<div class="feature-card" markdown>

### [Inbuilt Failure Handling](./exosphere/retry-policy.md)

Built-in retry policies with exponential backoff and jitter strategies for resilient, production-grade execution.

</div>

<div class="feature-card" markdown>

### [Infinite Parallel Agents](./exosphere/fanout.md)

Scale to unlimited parallel agents with automatic load distribution and dynamic fanout at runtime.

</div>

<div class="feature-card" markdown>

### [Dynamic Execution Graphs](./exosphere/concepts.md)

Durable execution designed for agentic flows with node based control of execution. 

</div>

<div class="feature-card" markdown>

### [Native State Persistence](./exosphere/store.md)

Persist workflow state across restarts and failures with graph-level key-value storage.

</div>

<div class="feature-card" markdown>

### [Observability](./exosphere/dashboard.md)

Visual monitoring, debugging, and management of workflows with real-time execution tracking.

</div>

</div>

Whether you're building data pipelines, AI agents, or complex workflow orchestrations, Exosphere provides the infrastructure backbone to make your AI applications production-ready and scalable.

---

**Watch the Step by Step Demo**:

<a href="https://www.youtube.com/watch?v=f41UtzInhp8" target="_blank">
  <img src="../assets/parallel-nodes-demo.png" alt="Step by Step Execution of an Exosphere Workflow">
</a>


---

## Run your first agent

<div class="feature-grid" style="grid-template-columns: repeat(2, 1fr);" markdown>

<div class="feature-card" markdown>

### [Getting Started](./getting-started.md)

Get the Exosphere State Manager and Dashboard running locally for development.

</div>

<div class="feature-card" markdown>

### [Run your first Node](./exosphere/register-node.md)

Create your first node and register it with the Exosphere runtime.

</div>

<div class="feature-card" markdown>

### [Trigger Agent](./exosphere/trigger-graph.md)

Learn how to trigger your agent workflows and manage execution flows.

</div>

<div class="feature-card" markdown>

### [Deploy & Monitor](./exosphere/dashboard.md)

Deploy your agents and monitor their execution with the visual dashboard.

</div>

</div>


## Open Source Commitment

We believe that humanity would not have been able to achieve the level of innovation and progress we have today without the support of open source and community, we want to be a part of this movement!

Please feel free to reach out to us at [nivedit@exosphere.host](mailto:nivedit@exosphere.host). Let's push the boundaries of possibilities for humanity together!

## Contributing

We welcome community contributions. For guidelines, refer to our [CONTRIBUTING.md](https://github.com/exospherehost/exospherehost/blob/main/CONTRIBUTING.md).

Thanks to our awesome contributors!
![exosphere.host Contributors](https://contrib.rocks/image?repo=exospherehost/exospherehost)
