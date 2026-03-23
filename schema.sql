-- SlideGen Database Schema
-- Generated: March 23, 2026
-- Database: SQLite 3
-- Purpose: Complete schema for SlideGen AI-powered presentation generator

-- ===========================================
-- USERS & AUTHENTICATION TABLES
-- ===========================================

-- Core users table with authentication and subscription management
CREATE TABLE IF NOT EXISTS users (
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
    cancel_at_period_end BOOLEAN DEFAULT 0
);

-- Extended user profile information
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    bio TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- User preferences and settings
CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    theme TEXT DEFAULT 'light',
    default_transition_enabled BOOLEAN DEFAULT 1,
    default_thank_you_enabled BOOLEAN DEFAULT 1,
    default_content_length TEXT DEFAULT 'standard',
    language TEXT DEFAULT 'en',
    settings_json TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ===========================================
-- PROJECT & CONTENT TABLES
-- ===========================================

-- User projects (documents/slides generated)
CREATE TABLE IF NOT EXISTS projects (
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

-- Individual slides within projects
CREATE TABLE IF NOT EXISTS slides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    slide_index INTEGER NOT NULL,  -- Order within project (0-based)
    slide_type TEXT NOT NULL,      -- 'intro', 'content', 'thank_you'
    title TEXT,
    content_text TEXT,             -- Plain text content
    html_content TEXT,             -- Generated HTML
    design_settings TEXT,          -- JSON: layout, colors, fonts
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Project-specific configuration and metadata
CREATE TABLE IF NOT EXISTS project_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER UNIQUE NOT NULL,
    slide_options TEXT,        -- JSON: slide generation options
    workflow_config TEXT,      -- JSON: workflow settings
    generation_params TEXT,    -- JSON: LLM parameters used
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- ===========================================
-- SUBSCRIPTION & BILLING TABLES
-- ===========================================

-- Promotional subscription codes management
CREATE TABLE IF NOT EXISTS subscription_codes (
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

-- Code redemption history and audit trail
CREATE TABLE IF NOT EXISTS code_redemptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    code TEXT NOT NULL,
    tier_granted TEXT NOT NULL,
    expires_at TIMESTAMP,
    redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ===========================================
-- ANALYTICS & LOGGING TABLES
-- ===========================================

-- Daily usage logs for analytics and debugging
CREATE TABLE IF NOT EXISTS daily_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    feature_type TEXT NOT NULL,  -- 'idea_generation', 'docx_upload', 'slide_export'
    feature_data TEXT,           -- JSON: additional context
    usage_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ===========================================
-- PERFORMANCE INDEXES
-- ===========================================

-- User-related indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_tier);

-- Project-related indexes
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);

-- Slide-related indexes
CREATE INDEX IF NOT EXISTS idx_slides_project_id ON slides(project_id);
CREATE INDEX IF NOT EXISTS idx_slides_type ON slides(slide_type);

-- Subscription-related indexes
CREATE INDEX IF NOT EXISTS idx_code_redemptions_user ON code_redemptions(user_id);

-- Analytics indexes
CREATE INDEX IF NOT EXISTS idx_usage_logs_user_date ON daily_usage_logs(user_id, usage_date);

-- ===========================================
-- DEFAULT DATA INSERTION
-- ===========================================

-- Insert default subscription codes
INSERT OR IGNORE INTO subscription_codes (code, tier, duration_days, max_uses, code_type)
VALUES ('SLIDEGENIUS', 'ultra', 30, -1, 'unlimited');

-- ===========================================
-- MIGRATION SCRIPTS (for existing databases)
-- ===========================================

-- Migration: Add code_type column to existing subscription_codes table
-- ALTER TABLE subscription_codes ADD COLUMN code_type TEXT DEFAULT 'limited';

-- Migration: Add cancel_at_period_end column to existing users table
-- ALTER TABLE users ADD COLUMN cancel_at_period_end BOOLEAN DEFAULT 0;

-- Migration: Update existing paid users with NULL expires_at to have 30-day expiry
-- UPDATE users SET subscription_expires_at = datetime('now', '+30 days')
-- WHERE subscription_tier != 'free' AND subscription_expires_at IS NULL;

-- Migration: Add default subscription fields to existing users
-- UPDATE users SET
--     subscription_tier = 'free',
--     daily_usage_reset_date = CURRENT_DATE,
--     idea_usage_today = 0,
--     docx_usage_today = 0
-- WHERE subscription_tier IS NULL;

-- ===========================================
-- SCHEMA DOCUMENTATION
-- ===========================================

/*
SCHEMA OVERVIEW:
- 9 core tables with proper normalization
- Foreign key constraints with CASCADE delete
- JSON fields for flexible metadata storage
- Comprehensive indexing for performance
- Subscription-based freemium model support

RELATIONSHIPS:
users (1) ──── (N) projects
projects (1) ──── (N) slides
projects (1) ──── (1) project_metadata
users (1) ──── (1) user_profiles
users (1) ──── (1) user_settings
users (1) ──── (N) code_redemptions
users (1) ──── (N) daily_usage_logs
subscription_codes (1) ──── (N) code_redemptions

SUBSCRIPTION TIERS:
- free: Limited usage (2 ideas/day, 3 docs/day, 20 slides max)
- plus: Medium usage (10 ideas/day, 10 docs/day, 20 slides max)
- ultra: Unlimited usage (-1 = no limits)

DATA TYPES:
- INTEGER: Auto-increment IDs, counts
- TEXT: Strings, JSON data, large content
- TIMESTAMP: Date/time with timezone support
- DATE: Date-only fields
- BOOLEAN: True/false flags

PERFORMANCE NOTES:
- SQLite WAL mode recommended for better concurrency
- Indexes on frequently queried columns
- Foreign key constraints ensure data integrity
- CASCADE delete maintains referential integrity

SCALABILITY CONSIDERATIONS:
- SQLite suitable for < 50 concurrent users
- Consider PostgreSQL migration for > 50 users
- Monitor table sizes and implement archival strategy
- Add connection pooling for high concurrency
*/