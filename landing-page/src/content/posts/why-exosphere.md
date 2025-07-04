---
title: "Why Exosphere: Revolutionizing Background AI Inference"
date: "2025-04-15"
author: "Exosphere Team"
authorRole: "AI Infrastructure Experts"
authorBio: "The Exosphere team is dedicated to making AI inference more accessible, efficient, and cost-effective for businesses of all sizes."
excerpt: "Discover how Exosphere is transforming background AI inference with its innovative satellite-based architecture, making it more affordable and developer-friendly than ever before."
coverImage: "/images/why-exosphere.png"
fileName: "why-exosphere.md"
---

# Why Exosphere?

As LLMs and custom models become core to modern products, companies are hitting a wall when it comes to scaling inference jobs, especially those that aren't real-time, but still mission-critical (like document processing, large-scale summarization, or daily analytics).

With Exosphere, we're making this effortless, affordable, and developer-friendly.

## Core Building Blocks

### Satellites
The smallest unit of computation in the Exosphere: designed to perform as a task which is:
- Atomic
- Idempotent
- Secure

Think of each satellite as a purpose-built microservice.

### Clusters
A group of satellites working together to complete a specific job.

**Example:** Need to extract structured JSON from a PDF in S3 via API and send it via webhook?

Your cluster might include:
- API Handler Satellite
- S3 File Reader
- OCR Satellite
- Text Extraction
- Gemma-3 Inference
- Schema Validator
- Webhook Output

### Orbit (open-sourcing soon!)
Our orchestrator that can scale horizontally across your compute (GPU/CPU, ARM/AMD—bring your infra or use ours). Orbit handles:

- Running satellites based on optimization strategies (cost, time, compute availability)
- Auto-scaling & reliability
- Out-of-the-box API server to manage pipelines, visualize logs, track failures, and monitor metrics
- Connect with exosphere or custom solutions for truly asynchronous tasks

## How It Works

You define (programmatically):
1. A trigger satellite (e.g., API call, CRON job, file upload)
2. An output satellite (e.g., Webhook, S3, Email)
3. A cluster of satellites in between to do the actual job

Each job comes with a Service Level Agreement (SLA) - for example, 10 minutes, 6 hours, or 24 hours. A higher SLA allows for better optimization, hence lower inference cost.

Exosphere's runtime system then finds the best configuration of compute nodes ("orbits") to execute the satellites, optimized for cost, security, and reliability.

## Unmatched Cost Efficiency

Because we run background inference, we can provide massive savings.

**Example:** Run DeepSeek-R1 inference at just $0.25 per million tokens (input + output) with a 6-hour SLA. That's:
- ~75% cheaper than Groq
- ~87% cheaper than most mainstream providers

## Think of Exosphere as...

A Firebase/Supabase-style Backend-as-a-Service, but purpose-built for background jobs and model orchestration, with a deep focus on inference and GPU-first workflows.

## Example Use Case: Understanding the Resume

![Resume Processing Workflow](/images/exo-diag1.png)

At a leading AI talent platform, the team receives hundreds of resumes daily. To make these resumes structured, searchable, and accessible for automated workflows, Aikin leverages Exosphere's DocumentAsJsonCluster - a powerful asynchronous pipeline designed for document-to-JSON conversion.

### Workflow Overview:
When resumes are uploaded to S3, Exosphere takes over via an API trigger. The satellite workflow retrieves the files, extracts raw text, runs OCR if necessary, and processes the content using a powerful LLM - DeepSeek-r1-70B - to generate structured JSON. The model output is validated against a pre-defined schema, with automatic re-prompting if validations fail. Once successful, the final JSON is delivered to a webhook endpoint, with minimal latency (typically around 4.5 seconds), while meeting a 5-minute SLA.

Exosphere intelligently deploys the model to the most cost-effective runtime while ensuring all SLA, security, and performance constraints are met.

### Developer Responsibilities at Aikin:
- Trigger the Exosphere Cluster API with the appropriate S3 paths, schema, and optional hint prompts.
- Implement a webhook to receive results, or use our Orbit API Server as a plug-and-play alternative.

Let Exosphere handle everything else, from cost optimization and model selection to SLA enforcement and data validation!

### What Team at Aikin Gets:
- JSON output in ~4.5 seconds (within a 5-minute SLA).
- Scalable and resilient infrastructure.
- Built-in logging, metrics, access control, billing, and analytics.
- And the best part, the lowest cost in the industry.

It's seriously that simple. Let Exosphere do the heavy lifting while you focus on building magic on top! 🥳 