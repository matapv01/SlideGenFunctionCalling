# SlideGen Database Schema Analysis

**Generated:** March 23, 2026  
**Database:** SQLite 3  
**Status:** Production-Ready with Scalability Concerns  

---

## Table of Contents

1. [Database Overview](#database-overview)
2. [Core Tables](#core-tables)
3. [User Management Tables](#user-management-tables)
4. [Project & Content Tables](#project--content-tables)
5. [Subscription & Billing Tables](#subscription--billing-tables)
6. [Analytics & Logging Tables](#analytics--logging-tables)
7. [Database Relationships](#database-relationships)
8. [Performance Analysis](#performance-analysis)
9. [Migration Strategy](#migration-strategy)

---

## Database Overview

### **Technology Stack**
- **Database:** SQLite 3 (file-based)
- **ORM:** None (raw SQL with sqlite3)
- **Connection:** Single file (`slidegen.db`)
- **Concurrency:** WAL mode enabled
- **Migrations:** Manual SQL scripts

### **Database File Location**
```
backend/infrastructure/database/slidegen.db
├── Size: ~1-10MB (depends on usage)
├── WAL mode: Enabled for better concurrency
├── Row factory: sqlite3.Row (dict-like access)
└── Connection: Context manager with auto-close
```

### **Initialization Flow**
```python
def init_db():
    # 1. Create all tables
    # 2. Create performance indexes
    # 3. Insert default subscription codes
    # 4. Run migration scripts
    # 5. Set default values for existing users
```

---

## Core Tables

### **1. Users Table** 🔑 **PRIMARY ENTITY**

**Purpose:** Core user authentication and subscription management

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    subscription_tier TEXT DEFAULT 'free',
    subscription_expires_at TIMESTAMP,
    daily_usage_reset_date DATE DEFAULT CURRENT_DATE,
    idea_usage_today INTEGER DEFAULT 0,
    docx_usage_today INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    cancel_at_period_end BOOLEAN DEFAULT 0  -- Added via migration
);
```

**Key Fields:**
- `subscription_tier`: 'free', 'plus', 'ultra'
- `subscription_expires_at`: NULL for permanent ultra, date for others
- `daily_usage_reset_date`: Tracks daily quota resets
- `idea_usage_today`: Daily idea generation count
- `docx_usage_today`: Daily document upload count
- `cancel_at_period_end`: Subscription cancellation flag

**Business Logic:**
```python
def get_daily_limits(self) -> Dict[str, int]:
    if self.subscription_tier == "free":
        return {"idea_generation": 2, "docx_upload": 3, "max_docx_slides": 20}
    elif self.subscription_tier == "plus":
        return {"idea_generation": 10, "docx_upload": 10, "max_docx_slides": 20}
    elif self.subscription_tier == "ultra":
        return {"idea_generation": -1, "docx_upload": -1, "max_docx_slides": -1}  # unlimited
```

---

### **2. Projects Table** 📁 **CONTENT CONTAINER**

**Purpose:** User projects (documents/slides generated)

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    source_type TEXT NOT NULL,  -- 'docx', 'idea'
    source_data TEXT,           -- JSON: original input data
    status TEXT DEFAULT 'draft', -- 'draft', 'processing', 'completed', 'failed'
    slide_count INTEGER DEFAULT 0,
    thumbnail_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Key Fields:**
- `source_type`: 'docx' (document upload) or 'idea' (prompt-based)
- `source_data`: JSON string with original input
- `status`: Workflow state tracking
- `slide_count`: Cached count for performance

**Relationships:**
- **1:N** with `slides` table
- **1:1** with `project_metadata` table
- **N:1** with `users` table

---

### **3. Slides Table** 📊 **CONTENT STORAGE**

**Purpose:** Individual slide content and metadata

```sql
CREATE TABLE slides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    slide_index INTEGER NOT NULL,  -- Order within project
    slide_type TEXT NOT NULL,      -- 'intro', 'content', 'thank_you'
    title TEXT,
    content_text TEXT,             -- Plain text content
    html_content TEXT,             -- Generated HTML
    design_settings TEXT,          -- JSON: layout, colors, fonts
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

**Key Fields:**
- `slide_index`: Ordering (0-based)
- `slide_type`: Content categorization
- `content_text`: Original text before HTML generation
- `html_content`: Final rendered HTML
- `design_settings`: JSON with styling preferences

**Data Flow:**
```
User Input → content_text → AI Processing → html_content + design_settings
```

---

## User Management Tables

### **4. User Profiles Table** 👤 **EXTENDED USER INFO**

**Purpose:** Additional user information (optional)

```sql
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    bio TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Usage:** Profile management, display names, avatars

---

### **5. User Settings Table** ⚙️ **USER PREFERENCES**

**Purpose:** User customization settings

```sql
CREATE TABLE user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    theme TEXT DEFAULT 'light',
    default_transition_enabled BOOLEAN DEFAULT 1,
    default_thank_you_enabled BOOLEAN DEFAULT 1,
    default_content_length TEXT DEFAULT 'standard',
    language TEXT DEFAULT 'en',
    settings_json TEXT,  -- Additional JSON settings
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Key Fields:**
- `theme`: 'light', 'dark'
- `default_transition_enabled`: Auto-add transition slides
- `default_thank_you_enabled`: Auto-add thank you slide
- `default_content_length`: 'short', 'standard', 'long'
- `settings_json`: Extensible JSON for future features

---

## Project & Content Tables

### **6. Project Metadata Table** 📋 **PROJECT CONFIGURATION**

**Purpose:** Store project-specific configuration and generation parameters

```sql
CREATE TABLE project_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER UNIQUE NOT NULL,
    slide_options TEXT,        -- JSON: slide generation options
    workflow_config TEXT,      -- JSON: workflow settings
    generation_params TEXT,    -- JSON: LLM parameters used
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

**Usage:**
- `slide_options`: Layout preferences, color schemes
- `workflow_config`: Which workflow version used
- `generation_params`: LLM temperature, model version, etc.

---

## Subscription & Billing Tables

### **7. Subscription Codes Table** 🎫 **PROMO CODE MANAGEMENT**

**Purpose:** Manage promotional subscription codes

```sql
CREATE TABLE subscription_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    tier TEXT NOT NULL,              -- 'plus', 'ultra'
    duration_days INTEGER DEFAULT 30,
    max_uses INTEGER DEFAULT 1,      -- -1 = unlimited
    current_uses INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    code_type TEXT DEFAULT 'limited', -- 'limited', 'unlimited'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Fields:**
- `code`: Unique promo code (e.g., 'SLIDEGENIUS')
- `tier`: Subscription level granted
- `max_uses`: Usage limit (-1 = unlimited)
- `code_type`: 'limited' or 'unlimited'

**Default Codes:**
```sql
INSERT OR IGNORE INTO subscription_codes (code, tier, duration_days, max_uses, code_type)
VALUES ('SLIDEGENIUS', 'ultra', 30, -1, 'unlimited');
```

---

### **8. Code Redemptions Table** 📝 **REDEMPTION HISTORY**

**Purpose:** Track code usage and redemption history

```sql
CREATE TABLE code_redemptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    code TEXT NOT NULL,
    tier_granted TEXT NOT NULL,
    expires_at TIMESTAMP,
    redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Usage:** Audit trail for subscription upgrades via promo codes

---

## Analytics & Logging Tables

### **9. Daily Usage Logs Table** 📊 **ANALYTICS & DEBUGGING**

**Purpose:** Track feature usage for analytics and debugging

```sql
CREATE TABLE daily_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    feature_type TEXT NOT NULL,  -- 'idea_generation', 'docx_upload', 'slide_export'
    feature_data TEXT,           -- JSON: additional context
    usage_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Usage:**
- Analytics: Feature usage patterns
- Debugging: Track failed operations
- Billing: Usage-based billing validation

---

## Database Relationships

### **Entity Relationship Diagram**

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   users     │────▶│user_profiles│     │user_settings│
│             │1    │             │1    │             │1
└─────────────┘     └─────────────┘     └─────────────┘
       │
       │ 1:N
       ▼
┌─────────────┐     ┌─────────────────┐
│  projects   │────▶│ project_metadata│
│             │1    │                 │1
└─────────────┘     └─────────────────┘
       │
       │ 1:N
       ▼
┌─────────────┐
│   slides    │
│             │
└─────────────┘

┌─────────────────┐     ┌──────────────────┐
│subscription_codes│◀────│code_redemptions │
│                 │     │                  │
└─────────────────┘     └──────────────────┘

┌─────────────┐
│daily_usage_ │
│    logs     │
│             │
└─────────────┘
```

### **Foreign Key Constraints**

| Table | Foreign Key | References | On Delete |
|-------|-------------|------------|-----------|
| `user_profiles` | `user_id` | `users.id` | CASCADE |
| `user_settings` | `user_id` | `users.id` | CASCADE |
| `projects` | `user_id` | `users.id` | CASCADE |
| `slides` | `project_id` | `projects.id` | CASCADE |
| `project_metadata` | `project_id` | `projects.id` | CASCADE |
| `code_redemptions` | `user_id` | `users.id` | CASCADE |
| `daily_usage_logs` | `user_id` | `users.id` | CASCADE |

**Cascade Behavior:** Deleting a user deletes all their projects, slides, and related data.

---

## Performance Analysis

### **Current Indexes** ⚡

```sql
-- Performance indexes (created in init_db)
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_slides_project_id ON slides(project_id);
CREATE INDEX idx_projects_updated_at ON projects(updated_at DESC);
CREATE INDEX idx_users_subscription ON users(subscription_tier);
CREATE INDEX idx_usage_logs_user_date ON daily_usage_logs(user_id, usage_date);
CREATE INDEX idx_code_redemptions_user ON code_redemptions(user_id);
```

**Index Coverage:**
- ✅ User projects listing (fast)
- ✅ Project slides loading (fast)
- ✅ Recent projects sorting (fast)
- ✅ Subscription tier queries (fast)
- ✅ Usage analytics queries (fast)

### **Query Performance**

**Fast Queries (indexed):**
```sql
-- Get user's recent projects: O(log n)
SELECT * FROM projects WHERE user_id = ? ORDER BY updated_at DESC LIMIT 50;

-- Get project slides: O(log n + k) where k = slide count
SELECT * FROM slides WHERE project_id = ? ORDER BY slide_index;
```

**Slow Queries (no index):**
```sql
-- Count all users: O(n) - full table scan
SELECT COUNT(*) FROM users;

-- Find projects by status: O(n) - no index on status
SELECT * FROM projects WHERE status = 'processing';
```

### **Concurrency Issues** 🚨 **CRITICAL**

**SQLite Limitations:**
```
├─ Single writer at a time
├─ WAL mode helps reads during writes
├─ But: Long-running slide generation blocks other operations
└─ Result: Database locks under concurrent load
```

**Problematic Scenarios:**
1. **User A** generates 50-slide presentation (4+ minutes)
2. **User B** tries to update profile → **BLOCKED**
3. **User C** uploads document → **BLOCKED**
4. **Result:** All users experience timeouts

---

## Migration Strategy

### **Current State → PostgreSQL Migration**

**Phase 1: Schema Migration**
```sql
-- SQLite → PostgreSQL type mapping
INTEGER → BIGINT (for IDs) / INTEGER (for counts)
TEXT → TEXT / VARCHAR(n)
TIMESTAMP → TIMESTAMP WITH TIME ZONE
BOOLEAN → BOOLEAN
DATE → DATE

-- Foreign keys: Same syntax
-- Indexes: CREATE INDEX syntax similar
-- Auto-increment: SERIAL instead of AUTOINCREMENT
```

**Phase 2: Data Migration**
```python
# Export from SQLite
sqlite_conn = sqlite3.connect('slidegen.db')
# Export all tables to JSON/CSV

# Import to PostgreSQL
pg_conn = psycopg2.connect('postgresql://...')
# Import with proper type conversion
```

**Phase 3: Application Changes**
```python
# Replace sqlite3 with psycopg2
# Update connection string
# Handle PostgreSQL-specific features:
# - Connection pooling
# - JSONB columns for metadata
# - Better concurrency
# - Real transactions
```

### **Migration Benefits**

| Aspect | SQLite (Current) | PostgreSQL (Target) |
|--------|------------------|---------------------|
| **Concurrency** | 1 writer, N readers | Multiple writers, high concurrency |
| **Performance** | Fast for small data | Scales to millions of rows |
| **Features** | Basic SQL | Advanced features (JSONB, arrays) |
| **Backup** | Manual file copy | pg_dump, point-in-time recovery |
| **Monitoring** | None | Rich statistics, query planner |
| **Scaling** | Single instance | Read replicas, sharding |

### **Migration Timeline**

```
Week 1-2: PostgreSQL setup + schema migration
Week 3: Data migration scripts
Week 4: Application code updates
Week 5: Testing + performance optimization
Week 6: Production deployment
```

---

## Database Size Estimation

### **Per User Storage**

| Table | Records/User | Size/Record | Total/User |
|-------|--------------|-------------|------------|
| `users` | 1 | ~200 bytes | ~200 bytes |
| `user_profiles` | 1 | ~500 bytes | ~500 bytes |
| `user_settings` | 1 | ~300 bytes | ~300 bytes |
| `projects` | ~10/month | ~1KB | ~10KB/month |
| `slides` | ~200/project | ~5KB | ~1MB/project |
| `project_metadata` | ~10/month | ~2KB | ~20KB/month |
| `daily_usage_logs` | ~50/month | ~200 bytes | ~10KB/month |
| **Total/User/Month** | | | **~1.1MB** |

### **System-wide Storage (1,000 users)**

| Time Period | Projects | Slides | Total Size |
|-------------|----------|--------|------------|
| **1 Month** | 10,000 | 2M | ~10GB |
| **6 Months** | 60,000 | 12M | ~60GB |
| **1 Year** | 120,000 | 24M | ~120GB |

### **Storage Optimization Strategies**

1. **Slide Content Compression**
   ```sql
   -- Store HTML as compressed blob
   html_content COMPRESSED TEXT
   ```

2. **Archive Old Projects**
   ```sql
   -- Move completed projects > 1 year to archive table
   CREATE TABLE projects_archive AS SELECT * FROM projects WHERE created_at < '2025-01-01';
   ```

3. **Cleanup Unused Data**
   ```sql
   -- Delete failed/draft projects older than 30 days
   DELETE FROM projects WHERE status IN ('failed', 'draft') AND created_at < datetime('now', '-30 days');
   ```

---

## Security Considerations

### **Data Protection**

| Risk | Current | Recommended |
|------|---------|-------------|
| **SQL Injection** | Parameterized queries ✅ | Same (psycopg2) |
| **Data Encryption** | None | Encrypt sensitive fields |
| **Access Control** | Application-level | Row-level security (PostgreSQL) |
| **Audit Logging** | Basic usage logs | Comprehensive audit trail |
| **Backup Security** | File copy | Encrypted backups |

### **Privacy Compliance**

- **GDPR:** User data deletion cascades properly
- **Data Retention:** No automatic cleanup (manual)
- **PII Fields:** Email, full_name, bio (consider encryption)

---

## Recommendations

### **Immediate Actions (1-2 weeks)**

1. **Add Missing Indexes**
   ```sql
   CREATE INDEX idx_projects_status ON projects(status);
   CREATE INDEX idx_slides_type ON slides(slide_type);
   CREATE INDEX idx_users_email ON users(email);  -- For login performance
   ```

2. **Implement Connection Pooling**
   ```python
   # For future PostgreSQL migration preparation
   # Current SQLite doesn't support pooling, but code structure ready
   ```

3. **Add Database Monitoring**
   ```python
   # Log slow queries (>100ms)
   # Monitor connection count
   # Track table sizes
   ```

### **Short-term (1-3 months)**

1. **PostgreSQL Migration** (highest priority)
2. **Add Data Archival** (cleanup old data)
3. **Implement Backup Strategy** (automated)
4. **Add Query Performance Monitoring**

### **Long-term (3-6 months)**

1. **Database Sharding** (if > 1M users)
2. **Read Replicas** (for analytics)
3. **Advanced Caching** (Redis layer)
4. **Real-time Analytics** (separate OLAP database)

---

## Summary

| Aspect | Rating | Notes |
|--------|--------|-------|
| **Schema Design** | ✅ Good | Well-normalized, clear relationships |
| **Performance** | 🟡 Moderate | Good indexes, but SQLite limits |
| **Scalability** | 🔴 Poor | SQLite single-writer bottleneck |
| **Maintainability** | ✅ Good | Clear table structure, good naming |
| **Data Integrity** | ✅ Good | Foreign keys, constraints |
| **Migration Ready** | 🟡 Partial | Schema portable, code needs updates |

**Critical Path:** Migrate to PostgreSQL within 3 months to support >50 concurrent users.

---

*Analysis Date: 2026-03-23*  
*Database: SQLite 3*  
*Tables: 9 core tables*  
*Estimated Migration Effort: 4-6 weeks*
