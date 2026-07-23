# SlideGen Project Analysis

**Generated:** March 23, 2026  
**Status:** Production-Ready with Scalability Concerns  
**Version:** 0.1.0  

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Workflow Architecture](#workflow-architecture)
3. [Tech Stack](#tech-stack)
4. [Infrastructure & Deployment](#infrastructure--deployment)
5. [Current Features](#current-features)
6. [Risks & Vulnerabilities](#risks--vulnerabilities)
7. [Scalability Problems](#scalability-problems)
8. [Recommendations](#recommendations)

---

## Project Overview

### Purpose

**SlideGen** is an AI-powered presentation generator that converts:
- Documents (DOCX, PDF) → HTML/PNG slides
- Ideas → Structured slide presentations

The system uses LangGraph orchestration, Gemini LLM (Google), and Playwright for rendering.

### Key Value Propositions

- One-click slide generation from documents
- AI-driven structure creation from ideas/prompts
- Subscription-based freemium model
- Fast HTML/PNG export pipeline
- Web-based UI (React + TypeScript)

---

## Workflow Architecture

### 1. **SlideGen Workflow** (Document → Slides)

**Entry Point:** `backend/workflows/slidegen_workflow/`

**Pipeline Stages:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    SlideGen Workflow Pipeline                   │
└─────────────────────────────────────────────────────────────────┘

1. CONVERT_DOCUMENT
   ├─ Input: DOCX/PDF file
   ├─ Uses: Docling (document parsing) / MarkItDown
   ├─ Output: Plain text + hierarchical document structure
   └─ ~5-30 seconds (depends on doc size)

2. ROUTE_AFTER_CONVERT (Router Node)
   ├─ If document has hierarchical structure (headings, sections)
   │  └─ Route → SPLIT_CONTENT
   └─ If plain text document
      └─ Route → AUTO_STRUCTURE_GENERATOR

3a. AUTO_STRUCTURE_GENERATOR (Optional)
   ├─ Input: Plain text
   ├─ Uses: Gemini LLM with function calling
   ├─ Task: Generate JSON structure (title, sections, subsections)
   ├─ Result: Creates structure for otherwise unstructured content
   └─ Cost: 1x LLM call

3b. SPLIT_CONTENT (Content Chunking)
   ├─ Input: Plain text + structure
   ├─ Logic: Split content into slides (char limits: 600-800 chars per slide)
   ├─ Rules:
   │  ├─ Respects hierarchical structure (headings = slide breaks)
   │  ├─ Splits large content into multiple slides
   │  └─ Max 800 chars per chunk (configurable)
   └─ Output: List of slide chunks

4. ORGANIZE_CHUNKS (Chunk Organization)
   ├─ Input: Raw slide chunks
   ├─ Task: Organize chunks for optimal presentation
   └─ Output: Structured slide queue

5. PLANNING_SLIDE (Slide Planning)
   ├─ Input: First chunk + full context
   ├─ Uses: Gemini LLM (function calling)
   ├─ Task: Generate slide design plan (title, layout, visual suggestions)
   ├─ Output: Slide metadata + design instructions
   └─ Parallel with: PROVIDE_NEXT_SLIDE

6. PROVIDE_NEXT_SLIDE (Queue Manager)
   ├─ Task: Extract next chunk from queue
   └─ Output: Next chunk for processing

7. GENERATE_SLIDE (Main Generation) - CRITICAL LOOP
   ├─ Input: Slide metadata + content
   ├─ Uses: Gemini LLM (function calling)
   ├─ Task: Generate slide HTML/structure with AI content
   ├─ Cost: 1x LLM call per slide
   ├─ Retry Logic:
   │  ├─ Max retries: 3 (configurable)
   │  ├─ On failure: Generate new slide
   │  └─ After max retries: Force accept
   └─ Output: Generated slide (title, bullet points, layout)

8. SLIDE_EVALUATOR (Quality Check) - VLM Decision
   ├─ Input: Generated slide + original content
   ├─ Uses: Gemini Vision LLM
   ├─ Task: Validate slide quality/relevance
   ├─ Decision: Accept/Deny
   └─ Router Logic: If DENY → back to step 7 (retry)

9. FINALIZE_SLIDE (Format Finalization)
   ├─ Input: Accepted slide
   ├─ Task: Apply formatting, templates
   └─ Output: Final slide object

10. HTML_RENDERER (Output Generation)
    ├─ Input: All finalized slides
    ├─ Uses: Playwright (headless Chrome)
    ├─ Task: Render slides to HTML/PNG format
    ├─ Time: ~2-5 seconds per slide
    └─ Output: ZIP file with HTML + PNG files

ROUTING DECISION:
├─ If more slides in queue → loop back to step 6
└─ If all slides processed → END (emit ZIP)
```

**Performance Characteristics:**
- LLM calls per slide: 2-3 (planning + generation + optional evaluator)
- Time per slide: 3-8 seconds (network + processing)
- Total time: O(n) where n = number of slides

---

### 2. **Idea Workflow** (Prompt → Structured Slides)

**Entry Point:** `backend/workflows/idea_workflow/`

**Pipeline:**

```
INPUT: User Prompt
  ↓
1. PROCESS_IDEA
   ├─ Input: Title + Prompt + Content Length + Flags (transition, thank you)
   ├─ Uses: Gemini LLM (function calling)
   ├─ Task: Generate slide structure from natural language
   ├─ Cost: 1x LLM call
   └─ Output: JSON with slide chunks

2. GENERATE_CALLBACK
   ├─ Task: Create callback structure
   └─ Output: Status updates

OUTPUT: JSON Structure (ready for SlideGen workflow)
```

**Difference from SlideGen:**
- SlideGen: Document → Structure (parsing)
- Idea: Prompt → Structure (AI generation)

---

## Tech Stack

### **Backend**

| Component | Technology | Purpose | Version |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | REST API, async request handling | 0.121.3+ |
| **Async Runtime** | Uvicorn | ASGI server | 0.38.0+ |
| **Orchestration** | LangGraph | Graph-based workflow execution | 0.2.x - 0.3.x |
| **LLM Integration** | LangChain | Main LLM framework | 0.3.x |
| **LLM Provider** | Gemini 2.5 Flash | Primary AI model | Flash (fastest) |
| **Document Parsing** | Docling + MarkItDown | DOCX/PDF parsing | Latest |
| **Web Scraping** | Playwright | Browser automation | 1.56.0+ |
| **Search Integration** | Tavily API | Web search capability | 0.7.21+ |
| **RAG/Retrieval** | FAISS | Vector search index | 1.13.0 (CPU) |
| **Database** | SQLite | User data, projects, subscriptions | Local file |
| **Authentication** | JWT + Python-Jose | Bearer token auth | 3.5.0+ |
| **File Upload** | Aiofiles | Async file operations | 23.2.0+ |
| **Security** | bcrypt | Password hashing | 5.0.0+ |

### **Frontend**

| Component | Technology | Purpose | Version |
|-----------|-----------|---------|---------|
| **Framework** | React | UI component library | 18.3.1 |
| **Build Tool** | Vite | Fast bundler + dev server | 7.3.1 |
| **Language** | TypeScript | Type safety | 5.8.3 |
| **UI Library** | shadcn/ui + Radix UI | Component system | Latest |
| **Styling** | Tailwind CSS | Utility-first CSS | 3.4.17 |
| **Routing** | React Router | Client-side navigation | 6.30.1 |
| **HTTP Client** | Native Fetch API | API calls | Built-in |
| **Testing** | Vitest | Unit/integration tests | 3.2.4 |

### **Infrastructure**

| Component | Technology | Purpose | Version |
|-----------|-----------|---------|---------|
| **Containerization** | Docker | Deployment packaging | 24+ |
| **Orchestration** | Docker Compose | Multi-container setup | v2 |
| **Reverse Proxy** | Nginx | Load balancing, static files | Latest alpine |
| **Python Version** | Python 3.11 | Backend runtime | 3.11 slim |
| **Node Version** | Node.js 22 | Frontend build | 22 alpine |
| **OS Base** | Alpine/Debian | Minimal images | Latest |

### **Third-Party APIs**

| Service | Purpose | Cost | Rate Limit |
|---------|---------|------|-----------|
| **Gemini API** | LLM calls (text + vision) | Pay-per-token | Unknown |
| **Tavily Search** | Web search results | Pay-per-search | ~3 keys configured |
| **Playwright** | Browser automation | Built-in | N/A |

---

## Infrastructure & Deployment

### **Docker Architecture**

```
docker-compose.yml
├── Service: nginx
│   ├─ Port: 80 (production), 12008 (dev)
│   ├─ Role: Reverse proxy, static file serving
│   └─ Depends on: slidegen service (health check)
│
└── Service: slidegen
    ├─ Build: Multi-stage (Node.js + Python)
    ├─ Port: 12008
    ├─ Environment: 
    │  ├─ .env file (API keys)
    │  ├─ EMBEDDING_DEVICE: cpu (FAISS)
    │  └─ DISABLE_CONVERTER: 0/1
    │
    ├─ Volumes:
    │  ├─ slidegen_db: SQLite database persistence
    │  ├─ slidegen_static: Generated files (outputs, uploads)
    │  └─ huggingface_cache: Model cache for embeddings
    │
    └─ Health Check: curl http://localhost:12008/health

Volumes (Named Persistence):
├── slidegen_db: Database files
├── slidegen_static: User outputs, captures
└── huggingface_cache: Downloaded ML models (~2-5GB)
```

### **Build Process**

```
Stage 1: Frontend Build
  └─ Node.js 22 → npm ci → npm run build → dist/

Stage 2: Python Dependencies
  └─ Poetry/uv → install deps → venv

Stage 3: Runtime Image
  └─ Combine frontend + Python → Final image (~3-5GB)

Build Time: 15-25 minutes (first run, ~3-5 minutes cached)
```

### **Deployment Flow**

```
Local Machine:
  git commit → git push

Server:
  git pull → docker compose up -d --build
  (Old .env, volumes untouched)
```

---

## Current Features

### **User Management**
- ✅ JWT authentication (Bearer token)
- ✅ User registration + email verification (schema exists)
- ✅ Subscription tiers (free, pro, enterprise)
- ✅ Rate limiting per endpoint
- ✅ Daily usage tracking (idea_usage_today, docx_usage_today)
- ✅ User profiles (name, avatar, bio)

### **Document Processing**
- ✅ DOCX upload and parsing (Docling)
- ✅ PDF support (via Docling)
- ✅ Hierarchical structure detection (headings → sections)
- ✅ Plain text document handling with auto-structuring
- ✅ Content chunking with configurable limits

### **AI Slide Generation**
- ✅ LLM-based slide content generation
- ✅ Slide evaluation + quality checking (VLM)
- ✅ Visual layout planning
- ✅ Retry logic for failed generations
- ✅ Template support

### **Idea-to-Slides**
- ✅ Prompt-based slide generation
- ✅ Content length customization (short, medium, long)
- ✅ Optional transition slides
- ✅ Optional thank-you slide

### **Export & Rendering**
- ✅ HTML export
- ✅ PNG screenshot generation (Playwright)
- ✅ ZIP package output
- ✅ Static file serving

### **Project Management**
- ✅ Create/save projects
- ✅ Project metadata (title, description, created date)
- ✅ Project listing
- ✅ Slide management within projects

### **Search & Tools**
- ✅ Tavily web search integration
- ✅ RAG with FAISS index
- ✅ Tool retrieval system

---

## Risks & Vulnerabilities

### **Security Risks**

| Risk | Severity | Details |
|------|----------|---------|
| **SQLite in Production** | 🔴 **HIGH** | SQLite not designed for concurrent production use; no built-in connection pooling; data loss risk under high load; no backup strategy visible |
| **API Keys in .env** | 🟡 **MEDIUM** | No encryption at rest; keys visible in container logs if not careful; no key rotation strategy |
| **JWT Secrets** | 🟡 **MEDIUM** | `SECRET_KEY` hardcoded requirement; no secret management system (HashiCorp Vault, AWS Secrets Manager) |
| **CORS Configuration** | 🟡 **MEDIUM** | Allows localhost:3000, :5173, :8080, :12008 → may expose API endpoints during development |
| **Input Validation** | 🟡 **MEDIUM** | Depends on Pydantic schemas; no visible rate limiting per IP (only per user); unauthenticated endpoints might be vulnerable |
| **File Upload Limits** | 🟡 **MEDIUM** | No visible file size limits; could allow DoS via large file uploads |
| **LLM Injection** | 🟡 **MEDIUM** | User input→LLM directly; potential prompt injection attacks through DOCX content or prompts |
| **Third-Party API Keys** | 🟡 **MEDIUM** | Tavily API keys exposed in .env; no rate limiting from external APIs |

### **Operational Risks**

| Risk | Severity | Details |
|------|----------|---------|
| **Single Container Instance** | 🔴 **HIGH** | No horizontal scaling; if container crashes, service down; no auto-restart policy for out-of-memory |
| **Database Size Growth** | 🟡 **MEDIUM** | SQLite file can grow unbounded; no archival/cleanup strategy visible; backups manual |
| **Disk Space** | 🟡 **MEDIUM** | HuggingFace cache can grow to 2-5GB; static files (outputs/uploads) unbounded; no cleanup strategy |
| **Memory Pressure** | 🔴 **HIGH** | Playwright (Chromium) + Python runtime + model loading; device can run out of memory under concurrent requests |
| **Timeout Handling** | 🟡 **MEDIUM** | Long-running workflows (10-30+ seconds per document); no visible timeout configuration; API calls might timeout |
| **Error Logging** | 🟡 **MEDIUM** | Errors logged to stdout; no centralized logging (no ELK, Datadog, CloudWatch); hard to debug in production |

### **Dependency Risks**

| Risk | Severity | Details |
|------|----------|---------|
| **Playwright Dependency** | 🟡 **MEDIUM** | Large binary (Chromium ~300MB); requires system libraries; can break on OS updates |
| **LLM Provider Lock-in** | 🟡 **MEDIUM** | Hard-coded to Gemini; changing LLM requires code refactoring |
| **LangGraph Stability** | 🟡 **MEDIUM** | LangGraph 0.2.x - 0.3.x (pre-release); API might change in future versions |

---

## Scalability Problems

### **1. Database Bottleneck** 🔴 CRITICAL

**Problem:**
```
SQLite Limitations:
├─ Single writer at a time (WAL mode helps, but still limited)
├─ No connection pooling
├─ All processes share same file on disk
├─ Under high concurrency: SQLITE_BUSY errors
├─ No data replication or backup
└─ Performance degrades with database file size
```

**Impact:**
- Max concurrent requests: ~5-10 (depending on query complexity)
- Beyond that: Database lock contention
- User deletion/updates can block slide generation

**Example Failure Scenario:**
```
User A is generating 50-slide presentation (slow)
User B tries to update profile → Blocked by User A's transaction
User C uploads new document → Blocked
→ All users experience timeouts
```

---

### **2. Single-Container Architecture** 🔴 CRITICAL

**Problem:**
```
Current: 1 Docker container (frontend + backend + workers)
├─ Backend: 1 Python process
│  ├─ CPU-bound: LLM calls (network-bound, but blocking)
│  ├─ Memory: HuggingFace models (~2GB) + Playwright (~500MB)
│  └─ Threads: Single async event loop
│
├─ Worker: None (in-process)
└─ Load Balancer: Nginx (single backend instance → no distribution)

Result: 
├─ 10 concurrent requests → CPU/memory saturation
├─ 20 concurrent requests → Process crashes or timeout
└─ No failover, no horizontal scaling
```

**Impact:**
- Linear performance degradation with users
- One spike → entire service down
- Can't scale beyond single machine capacity

---

### **3. Synchronous I/O Bottleneck** 🟡 HIGH

**Problem:**
```
Current Workflow (per slide generation):
1. Gemini LLM call: ~2-5 seconds (network blocked)
2. VLM evaluation: ~1-3 seconds (network blocked)
3. Total: ~3-8 seconds per slide

For 50-slide document:
├─ Total time: 50 × 5 seconds = 250 seconds (4+ minutes)
├─ All requests are blocking
├─ FastAPI async helps, but LLM calls are still I/O bound
└─ Multiple concurrent users → request queue buildup
```

**Impact:**
- Average latency: 4+ minutes per document
- Under load: exponential latency increase
- Users perceive service as "slow" or "broken"

---

### **4. Memory Pressure** 🟡 HIGH

**Problem:**
```
Per Container Memory Usage:
├─ Python base: ~100-150MB
├─ FastAPI + dependencies: ~150-200MB
├─ HuggingFace models (loaded on first use): ~2GB
├─ Playwright Chromium: ~500MB per instance
├─ Output rendering (PIL, XML parsing): ~200-500MB
└─ Total per container: ~3-4GB

Concurrent Request Scenario:
├─ 5 concurrent slide generations
├─ Each uses Playwright instance
├─ All share model cache
└─ Memory: 3GB + (5 × 200MB) = 4GB+ → OOM Kill
```

**Impact:**
- Container crashes under moderate concurrent load
- No graceful degradation
- Lost in-flight requests

---

### **5. LLM API Rate Limiting** 🟡 HIGH

**Problem:**
```
Gemini API Rate Limits (shared account):
├─ Requests per second: ~10 (varies by tier)
├─ Tokens per minute: ~1M (varies)
├─ Current app: No backoff/retry strategy visible
├─ If limit hit: 429 Too Many Requests → workflow fails
└─ No queue system (first-come-first-served)
```

**Impact:**
- 10 concurrent users → API hits rate limit
- No fair scheduling (some users' requests get dropped)
- Need separate API keys or quota management

---

### **6. Disk I/O Bottleneck** 🟡 MEDIUM

**Problem:**
```
Disk Write Pattern:
├─ Each document: upload to /static/uploads
├─ Output: /static/output (generated HTML/PNG files)
├─ Example: 50-slide document
│  ├─ 50 HTML files: ~500KB total
│  ├─ 50 PNG files: ~2-5MB each = 100-250MB
│  └─ ZIP output: ~100-250MB
│
└─ Concurrent 5 users:
   └─ Writing 1.25GB to disk simultaneously
```

**Impact:**
- Disk I/O contention
- Slower rendering on slower storage (spinning disk)
- Database .db file also on same disk
- Container death on no disk space

---

### **7. Rendering Pipeline Bottleneck** 🟡 MEDIUM

**Problem:**
```
Playwright Rendering (HTML → PNG):
├─ Per slide: ~2-5 seconds
├─ Requires full browser instance: ~500MB memory
├─ Sequential: Slides rendered one-by-one
├─ Concurrent slides: Can't share browser instance safely
└─ 50 slides: 50 × 3 seconds = 150+ seconds
```

**Impact:**
- Export takes 2-5 minutes per document
- Memory pressure (can't parallelize safely)
- High CPU usage (rendering is CPU-intensive)

---

### **8. No Request Queuing or Backpressure** 🟡 MEDIUM

**Problem:**
```
Current Flow:
User → FastAPI → Workflow execution (blocking LLM calls)

Under Load:
├─ FastAPI accepts all requests (no queue)
├─ All requests start execution simultaneously
├─ Memory/CPU overwhelmed
├─ Requests fail or timeout
└─ No prioritization (free vs paid users)
```

**Impact:**
- Free users can block paid users
- No service level guarantees
- Thundering herd problem

---

### **Summary: Scalability Limits**

```
Current Architecture Capacity:

┌─────────────────────────────────────────────┐
│  Realistic Capacity per Container           │
├─────────────────────────────────────────────┤
│ Concurrent Users:           5-10            │
│ Documents/hour:             50-100          │
│ Average Slides/document:    30-50           │
│ Avg Response Time:          4-6 minutes     │
│ Max QPS (requests/sec):     2-3             │
│ Memory Required:            4-6GB           │
│ CPU Required:               2-4 cores       │
│ Storage:                    10GB+ (outputs) │
└─────────────────────────────────────────────┘

To reach 1000+ concurrent users:
├─ Need 100+ containers (horizontal scaling)
├─ Need PostgreSQL or similar (not SQLite)
├─ Need Redis or Celery for task queuing
├─ Need separate LLM/Playwright worker pools
└─ Infrastructure cost: 10-50x current
```

---

## Recommendations

### **Priority 1: Immediate Actions** (1-2 weeks)

1. **Replace SQLite with PostgreSQL**
   ```sql
   -- Migration: SQLite → PostgreSQL
   ├─ Use connection pooling (psycopg2 + connection pool)
   ├─ Test with 20+ concurrent connections
   └─ Add automated backups (pg_dump daily)
   ```

2. **Add Request Queuing (Celery + Redis)**
   ```python
   # Replace in-process workflow with queued tasks
   User Request → Celery Queue → Worker Pool → Result
   ├─ Non-blocking API responses
   ├─ Background slide generation
   ├─ Prioritization support
   └─ Retry logic built-in
   ```

3. **Implement Job Retry Logic**
   - Add exponential backoff for LLM calls
   - Handle 429 (rate limit) gracefully
   - Maximum retry attempts with logging

4. **Add Logging & Monitoring**
   - Structure logs (JSON format)
   - Send to CloudWatch / ELK
   - Alerts for errors, timeouts
   - Metrics: LLM call duration, queue length

### **Priority 2: Short-Term (1-2 months)**

1. **Separate Worker Pool**
   ```
   ├─ API Container: FastAPI + authentication only
   ├─ Worker Container(s): Celery workers (horizontal scale)
   ├─ Redis: Message queue + cache
   └─ PostgreSQL: Persistent state
   ```

2. **Implement Caching**
   ```
   ├─ Redis cache for user profiles, project metadata
   ├─ Cache LLM responses (same prompt = same output)
   ├─ Cache document structures (same DOCX = same parse)
   └─ TTL: 24 hours for structures, 7 days for LLM
   ```

3. **Optimize Rendering**
   ```
   ├─ Use browser pool instead of sequential rendering
   ├─ Batch slides for rendering (multi-page PDF)
   └─ Consider SVG export instead of PNG (smaller, faster)
   ```

4. **Add Rate Limiting per IP**
   ```python
   # Current: Per-user rate limiting
   # Add: Per-IP rate limiting (prevent abuse)
   ├─ 100 requests/hour per IP
   ├─ 1000 requests/hour per authenticated user
   └─ Exponential backoff on repeated violations
   ```

### **Priority 3: Medium-Term (2-3 months)**

1. **Multi-Model LLM Support**
   ```
   ├─ Gemini (current)
   ├─ GPT-4 (OpenAI) - fallback
   ├─ Claude (Anthropic) - option
   └─ Switch based on availability/cost
   ```

2. **Cost Optimization**
   ```
   ├─ Cheaper models for non-critical tasks (text analysis)
   ├─ Batch API calls (reduce request count)
   ├─ Cache common structures
   └─ Monitor LLM spending per user
   ```

3. **User Resource Quotas**
   ```
   ├─ Free tier: 5 documents/month, 50 slides/month
   ├─ Pro tier: 50 documents/month, 500 slides/month
   ├─ Enterprise: Unlimited
   └─ Enforce via rate limiter + database tracking
   ```

4. **Document Size Limits**
   ```
   ├─ Max file size: 50MB
   ├─ Max slides output: 200 per document
   └─ Break large docs into chunks (multi-upload)
   ```

### **Priority 4: Long-Term (3-6 months)**

1. **Kubernetes Deployment**
   ```
   ├─ Replace Docker Compose with Helm charts
   ├─ Auto-scaling based on CPU/memory/queue length
   ├─ Rolling updates (zero downtime)
   ├─ Multi-region deployment (CDN)
   └─ Service mesh (Istio) for observability
   ```

2. **Advanced Caching Strategy**
   ```
   ├─ Content-addressable cache (SHA256 hash)
   ├─ Separate cache layers: HTTP, application, database
   ├─ Cache invalidation strategy
   └─ Distributed cache (Redis Cluster)
   ```

3. **Separate LLM Provider Service**
   ```
   ├─ Dedicated service: LLM API calls only
   ├─ Request deduplication
   ├─ Response caching
   ├─ Rate limit negotiation
   └─ Cost attribution per user
   ```

4. **Analytics & Insights**
   ```
   ├─ Track user behavior (which features used)
   ├─ Monitor LLM output quality
   ├─ A/B testing framework
   ├─ Cost per user calculation
   └─ Predictive scaling based on trends
   ```

---

## Architecture Recommendations

### **Recommended Production Architecture**

```
┌──────────────────────────────────────────────────────────┐
│                   Load Balancer (Nginx)                  │
└───┬─────────────────────────┬──────────────────────┬─────┘
    │                         │                      │
    ▼                         ▼                      ▼
┌────────────┐         ┌────────────┐         ┌────────────┐
│  API Pod 1 │         │  API Pod 2 │         │  API Pod N │
│  (FastAPI) │         │  (FastAPI) │         │  (FastAPI) │
└─────┬──────┘         └─────┬──────┘         └─────┬──────┘
      │                      │                      │
      └──────────────┬───────┴──────────────┬───────┘
                     │                      │
                ┌────▼────────────┐   ┌─────▼───────┐
                │   Redis Queue   │   │ PostgreSQL  │
                │  + Cache Store  │   │  Database   │
                └────┬────────────┘   └─────────────┘
                     │
      ┌──────────────┴──────────────┐
      ▼                             ▼
┌─────────────┐             ┌──────────────┐
│Worker Pod 1 │             │Worker Pod N  │
│(Celery)     │             │(Celery)      │
│- LLM calls  │             │- Rendering   │
│- File ops   │             │- Conversion  │
└─────────────┘             └──────────────┘

Benefits:
├─ Horizontal scaling (add more API/Worker pods)
├─ Decoupled concerns (API vs background tasks)
├─ Better fault tolerance (pod crashes don't affect others)
├─ Resource isolation (workers can use more memory)
└─ Cost efficiency (scale per workload type)
```

### **Database Migration Path**

```
Current: SQLite (3 MB file)
  ↓
Step 1: PostgreSQL locally + SQLite backup
  ├─ Import historical data
  ├─ Test concurrent connections
  └─ Validate data integrity

Step 2: PostgreSQL in container (compose)
  ├─ Add persistence volume
  ├─ Regular backups (pg_dump)
  └─ Connection pooling (pgBouncer)

Step 3: Managed PostgreSQL (RDS/Azure)
  ├─ Replication for HA
  ├─ Automated backups
  └─ Read replicas for analytics
```

---

## Summary State

| Aspect | Status | Readiness |
|--------|--------|-----------|
| **MVP Functionality** | ✅ Complete | Production |
| **Code Quality** | ✅ Good | Maintainable |
| **Documentation** | 🟡 Partial | Needs API docs |
| **Testing** | 🟡 Minimal | Unit tests needed |
| **Scalability** | 🔴 Limited | Single container only |
| **Security** | 🟡 Moderate | API keys, auth in place |
| **Monitoring** | 🔴 Missing | No observability |
| **Deployment** | ✅ Good | Docker + Compose |
| **Cost** | ✅ Low | Free tier LLMs feasible |
| **Production Ready** | 🟡 Partial | For <50 concurrent users |

---

## Implementation Effort Estimate

| Phase | Duration | Effort | Risk |
|-------|----------|--------|------|
| **PostgreSQL Migration** | 1-2 weeks | Medium | Low |
| **Celery + Redis Setup** | 2-3 weeks | High | Medium |
| **Worker Pool + Scaling** | 3-4 weeks | High | Medium |
| **Monitoring + Logging** | 1-2 weeks | Low | Low |
| **Load Testing & Optimization** | 2-3 weeks | Medium | Low |
| **Kubernetes Migration** | 4-6 weeks | Very High | High |

**Total Estimated Effort:** 3-5 months  
**Recommended Prioritization:** SQLite → PostgreSQL → Celery → Kubernetes

---

## Conclusion

**SlideGen** is a well-architected MVP with solid foundations:
- ✅ Clean separation of concerns (API, services, workflows)
- ✅ Good async/await patterns (FastAPI, async services)
- ✅ Logical workflow design (LangGraph state machines)
- ✅ Reasonable tech stack choices

**However, critical scalability issues prevent production deployment beyond ~50 concurrent users:**
- 🔴 SQLite is a hard blocker for multi-user systems
- 🔴 Single-container architecture limits horizontal scaling
- 🔴 No request queuing or backpressure handling
- 🔴 Memory/CPU pressure under load

**Recommendation:** Address Priority 1 items (PostgreSQL, Celery) before scaling beyond pilot customers. This will unlock 10-100x capacity improvement and set foundation for Kubernetes scaling.

---

*Analysis Date: 2026-03-23*  
*Workspace: `/home/trevor/Code/space/SlideGenFunctionCalling`*
