-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- CORE TABLES WITH VECTOR EMBEDDINGS
-- ============================================================================

-- Users table
CREATE TABLE user_id (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- User profiles with vector embedding
CREATE TABLE users_profile (
    profile_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES user_id(user_id) ON DELETE CASCADE,
    username VARCHAR(100) UNIQUE,
    full_name VARCHAR(255),
    bio TEXT,
    avatar_url VARCHAR(500),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    profile_embedding vector(384)
);

CREATE INDEX idx_profile_embedding ON users_profile 
USING ivfflat (profile_embedding vector_cosine_ops) WITH (lists = 100);

-- User preferences
CREATE TABLE users_preferences (
    preference_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES user_id(user_id) ON DELETE CASCADE,
    learning_style VARCHAR(100),
    preferred_subjects TEXT,
    difficulty_level VARCHAR(50),
    study_time_preference VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    preference_embedding vector(384)
);

CREATE INDEX idx_preference_embedding ON users_preferences 
USING ivfflat (preference_embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================================
-- RESOURCE TABLES
-- ============================================================================

CREATE TABLE resources_metadata (
    resource_id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    resource_type VARCHAR(100),
    difficulty_level VARCHAR(50),
    file_size_mb FLOAT,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploader_user_id INT REFERENCES user_id(user_id),

    metadata_embedding vector(384)
);


CREATE INDEX idx_metadata_embedding ON resources_metadata 
USING ivfflat (metadata_embedding vector_cosine_ops) WITH (lists = 100);

CREATE TABLE resources_content (
    content_id SERIAL PRIMARY KEY,
    resource_id INT UNIQUE REFERENCES resources_metadata(resource_id) ON DELETE CASCADE,
    file_path VARCHAR(500),
    file_url VARCHAR(500),
    mime_type VARCHAR(100),
    page_count INT,
    duration_seconds INT,
    storage_location VARCHAR(500),
    checksum VARCHAR(255),

    content_embedding vector(768),
    text_embedding vector(384),
    visual_embedding vector(512)
);

CREATE INDEX idx_content_embedding ON resources_content 
USING ivfflat (content_embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_text_embedding ON resources_content 
USING ivfflat (text_embedding vector_cosine_ops) WITH (lists = 100);

CREATE TABLE resources_chunks (
    chunk_id SERIAL PRIMARY KEY,
    resource_id INT REFERENCES resources_metadata(resource_id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_order INT,
    page_number INT,
    start_position INT,
    end_position INT,

    chunk_embedding vector(384),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chunk_embedding ON resources_chunks 
USING ivfflat (chunk_embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_resource_chunks ON resources_chunks(resource_id, chunk_order);

CREATE TABLE resources_stats (
    stat_id SERIAL PRIMARY KEY,
    resource_id INT UNIQUE REFERENCES resources_metadata(resource_id) ON DELETE CASCADE,
    view_count INT DEFAULT 0,
    download_count INT DEFAULT 0,
    favorite_count INT DEFAULT 0,
    average_rating FLOAT,
    rating_count INT DEFAULT 0,
    last_accessed TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TAGS
-- ============================================================================

CREATE TABLE tags_master (
    tag_id SERIAL PRIMARY KEY,
    tag_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100),
    usage_counter INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    tag_embedding vector(384)
);

CREATE INDEX idx_tag_embedding ON tags_master 
USING ivfflat (tag_embedding vector_cosine_ops) WITH (lists = 100);

CREATE TABLE mapping_resource_tags (
    mapping_id SERIAL PRIMARY KEY,
    resource_id INT REFERENCES resources_metadata(resource_id) ON DELETE CASCADE,
    tag_id INT REFERENCES tags_master(tag_id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    added_by_user_id INT REFERENCES user_id(user_id),
    confidence FLOAT,

    UNIQUE(resource_id, tag_id)
);

CREATE INDEX idx_resource_tags ON mapping_resource_tags(resource_id);
CREATE INDEX idx_tag_resources ON mapping_resource_tags(tag_id);

CREATE TABLE mapping_user_interests (
    mapping_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES user_id(user_id) ON DELETE CASCADE,
    tag_id INT REFERENCES tags_master(tag_id) ON DELETE CASCADE,
    interest_level VARCHAR(50),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP,

    UNIQUE(user_id, tag_id)
);

CREATE INDEX idx_user_interests ON mapping_user_interests(user_id);

-- ============================================================================
-- ACTIVITY TABLES
-- ============================================================================

CREATE TABLE activites_views (
    view_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES user_id(user_id) ON DELETE CASCADE,
    resource_id INT REFERENCES resources_metadata(resource_id) ON DELETE CASCADE,
    view_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    view_duration_seconds INT,
    device_type VARCHAR(50),

    session_context_embedding vector(128)
);

CREATE INDEX idx_views_user ON activites_views(user_id, view_timestamp DESC);
CREATE INDEX idx_views_resource ON activites_views(resource_id);

CREATE INDEX idx_session_context ON activites_views 
USING ivfflat (session_context_embedding vector_cosine_ops) WITH (lists = 50);

CREATE TABLE activites_downloads (
    download_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES user_id(user_id) ON DELETE CASCADE,
    resource_id INT REFERENCES resources_metadata(resource_id) ON DELETE CASCADE,
    download_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    filesize_downloaded INT,
    download_success BOOLEAN DEFAULT true
);

CREATE INDEX idx_downloads_user ON activites_downloads(user_id);
CREATE INDEX idx_downloads_resource ON activites_downloads(resource_id);

CREATE TABLE activites_ratings (
    rating_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES user_id(user_id) ON DELETE CASCADE,
    resource_id INT REFERENCES resources_metadata(resource_id) ON DELETE CASCADE,
    rating_value INT CHECK (rating_value BETWEEN 1 AND 5),
    review_text TEXT,
    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    review_sentiment_embedding vector(384),

    UNIQUE(user_id, resource_id)
);

CREATE INDEX idx_ratings_user ON activites_ratings(user_id);
CREATE INDEX idx_ratings_resource ON activites_ratings(resource_id);

CREATE INDEX idx_review_sentiment ON activites_ratings 
USING ivfflat (review_sentiment_embedding vector_cosine_ops) WITH (lists = 50);

-- ============================================================================
-- RECOMMENDATION TABLES
-- ============================================================================

CREATE TABLE recommendations_generated (
    recommendation_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES user_id(user_id) ON DELETE CASCADE,
    resource_id INT REFERENCES resources_metadata(resource_id) ON DELETE CASCADE,
    algorithm_used VARCHAR(100),
    confidence_score FLOAT,
    reason TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    position INT,

    recommendation_embedding vector(384),

    CONSTRAINT unique_user_resource_rec UNIQUE(user_id, resource_id, generated_at)
);

CREATE INDEX idx_recommendations_user ON recommendations_generated(user_id, generated_at DESC);
CREATE INDEX idx_recommendations_score ON recommendations_generated(user_id, confidence_score DESC);

CREATE INDEX idx_recommendation_embedding ON recommendations_generated 
USING ivfflat (recommendation_embedding vector_cosine_ops) WITH (lists = 100);

CREATE TABLE recommendations_feedback (
    feedback_id SERIAL PRIMARY KEY,
    recommendation_id INT UNIQUE REFERENCES recommendations_generated(recommendation_id) ON DELETE CASCADE,
    user_id INT REFERENCES user_id(user_id) ON DELETE CASCADE,
    was_clicked BOOLEAN DEFAULT false,
    was_helpful BOOLEAN,
    feedback_type VARCHAR(50),
    feedback_text TEXT
);

CREATE INDEX idx_feedback_user ON recommendations_feedback(user_id);

-- ============================================================================
-- OTHER HELPER TABLES
-- ============================================================================

CREATE TABLE search_queries (
    query_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES user_id(user_id),
    query_text TEXT NOT NULL,
    query_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    results_count INT,

    query_embedding vector(384)
);

CREATE INDEX idx_query_embedding ON search_queries 
USING ivfflat (query_embedding vector_cosine_ops) WITH (lists = 50);

CREATE TABLE user_resource_interactions (
    interaction_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES user_id(user_id) ON DELETE CASCADE,
    resource_id INT REFERENCES resources_metadata(resource_id) ON DELETE CASCADE,
    interaction_type VARCHAR(50),
    interaction_score FLOAT,
    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    interaction_embedding vector(256),

    UNIQUE(user_id, resource_id)
);

CREATE INDEX idx_interaction_embedding ON user_resource_interactions 
USING ivfflat (interaction_embedding vector_cosine_ops) WITH (lists = 100);
