admin-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- CORE TABLES WITH VECTOR EMBEDDINGS
-- ============================================================================

-- Users table with profile embedding for user similarity
CREATE TABLE user_id (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- User profiles with vector embedding for matching similar users
CREATE TABLE users_profile (
    profile_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES user_id(user_id) ON DELETE CASCADE,
    username VARCHAR(100) UNIQUE,
    full_name VARCHAR(255),
    bio TEXT,
    avatar_url VARCHAR(500),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Vector embedding for user profile (based on bio, interests, behavior)
    profile_embedding vector(384),  -- 384-dim for sentence-transformers
    
    -- Index for similarity search
    CONSTRAINT users_profile_user_id_fkey FOREIGN KEY (user_id) REFERENCES user_id(use
);

CREATE INDEX idx_profile_embedding ON users_profile 
USING ivfflat (profile_embedding vector_cosine_ops) WITH (lists = 100);

-- User preferences with learning style embedding
CREATE TABLE users_preferences (
    preference_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES user_id(user_id) ON DELETE CASCADE,
    learning_style VARCHAR(100),
    preferred_subjects TEXT,  -- JSON array
    difficulty_level VARCHAR(50),
    study_time_preference VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Vector for learning preferences (for personalized recommendations)
    preference_embedding vector(384)
);

CREATE INDEX idx_preference_embedding ON users_preferences 
USING ivfflat (preference_embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================================
-- RESOURCE TABLES WITH CONTENT EMBEDDINGS
-- ============================================================================

-- Resources metadata with title/description embedding
CREATE TABLE resources_metadata (
    resource_id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    resource_type VARCHAR(100),
    difficulty_level VARCHAR(50),
    file_size_mb FLOAT,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploader_user_id INT REFERENCES user_id(user_id),
    
    -- Vector embedding for resource metadata (title + description)
    metadata_embedding vector(384),
    
    CONSTRAINT resources_metadata_uploader_fkey FOREIGN KEY (uploader_user_id) 
        REFERENCES user_id(user_id)
);

CREATE INDEX idx_metadata_embedding ON resources_metadata 
USING ivfflat (metadata_embedding vector_cosine_ops) WITH (lists = 100);

-- Resources content with full content embedding
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
    
    -- Vector embedding for full content (chunked and aggregated)
    content_embedding vector(768),  -- Larger dimension for richer content representation
    
    -- Additional embeddings for multi-modal content
    text_embedding vector(384),      -- Text content only
    visual_embedding vector(512)     -- For images/diagrams (optional)
);

CREATE INDEX idx_content_embedding ON resources_content 
USING ivfflat (content_embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_text_embedding ON resources_content 
USING ivfflat (text_embedding vector_cosine_ops) WITH (lists = 100);

-- Resource chunks for detailed semantic search within documents
CREATE TABLE resources_chunks (
    chunk_id SERIAL PRIMARY KEY,
    resource_id INT REFERENCES resources_metadata(resource_id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_order INT,
    page_number INT,
    start_position INT,
    end_position INT,
    
    -- Vector embedding for each chunk
    chunk_embedding vector(384),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chunk_embedding ON resources_chunks 
USING ivfflat (chunk_embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_resource_chunks ON resources_chunks(resource_id, chunk_order);

-- Resource statistics
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
-- TAGS AND CATEGORIZATION
-- ============================================================================

-- Tags with tag embedding for semantic tag similarity
CREATE TABLE tags_master (
    tag_id SERIAL PRIMARY KEY,
    tag_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100),
    usage_counter INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Vector embedding for tag semantic meaning
    tag_embedding vector(384)
);

CREATE INDEX idx_tag_embedding ON tags_master 
USING ivfflat (tag_embedding vector_cosine_ops) WITH (lists = 100);

-- Mapping between resources and tags
CREATE TABLE mapping_resource_tags (
    mapping_id SERIAL PRIMARY KEY,
    resource_id INT REFERENCES resources_metadata(resource_id) ON DELETE CASCADE,
    tag_id INT REFERENCES tags_master(tag_id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    added_by_user_id INT REFERENCES user_id(user_id),
    confidence FLOAT,  -- For auto-generated tags
    
    UNIQUE(resource_id, tag_id)
);

CREATE INDEX idx_resource_tags ON mapping_resource_tags(resource_id);
CREATE INDEX idx_tag_resources ON mapping_resource_tags(tag_id);

-- User interest mapping with weighted embeddings
CREATE TABLE mapping_user_interests (
    mapping_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES user_id(user_id) ON DELETE CASCADE,
    tag_id INT REFERENCES tags_master(tag_id) ON DELETE CASCADE,
    interest_level VARCHAR(50),  -- 'high', 'medium', 'low'
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP,
    
    UNIQUE(user_id, tag_id)
);

CREATE INDEX idx_user_interests ON mapping_user_interests(user_id);

-- ============================================================================
-- ACTIVITY TRACKING WITH CONTEXTUAL EMBEDDINGS
-- ============================================================================

-- Activity views with session context embedding
CREATE TABLE activites_views (
    view_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES user_id(user_id) ON DELETE CASCADE,
    resource_id INT REFERENCES resources_metadata(resource_id) ON DELETE CASCADE,
    view_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    view_duration_seconds INT,
    device_type VARCHAR(50),
    
    -- Context embedding (captures viewing context and behavior patterns)
    session_context_embedding vector(128)
);

CREATE INDEX idx_views_user ON activites_views(user_id, view_timestamp DESC);
CREATE INDEX idx_views_resource ON activites_views(resource_id);
CREATE INDEX idx_session_context ON activites_views 
USING ivfflat (session_context_embedding vector_cosine_ops) WITH (lists = 50);

-- Activity downloads
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

-- Activity ratings with sentiment embedding
CREATE TABLE activites_ratings (
    rating_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES user_id(user_id) ON DELETE CASCADE,
    resource_id INT REFERENCES resources_metadata(resource_id) ON DELETE CASCADE,
    rating_value INT CHECK (rating_value BETWEEN 1 AND 5),
    review_text TEXT,
    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Sentiment embedding from review text
    review_sentiment_embedding vector(384),
    
    UNIQUE(user_id, resource_id)
);

CREATE INDEX idx_ratings_user ON activites_ratings(user_id);
CREATE INDEX idx_ratings_resource ON activites_ratings(resource_id);
CREATE INDEX idx_review_sentiment ON activites_ratings 
USING ivfflat (review_sentiment_embedding vector_cosine_ops) WITH (lists = 50);

-- ============================================================================
-- RECOMMENDATIONS WITH HYBRID EMBEDDINGS
-- ============================================================================

-- Generated recommendations with composite embedding
CREATE TABLE recommendations_generated (
    recommendation_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES user_id(user_id) ON DELETE CASCADE,
    resource_id INT REFERENCES resources_metadata(resource_id) ON DELETE CASCADE,
    algorithm_used VARCHAR(100),  -- 'collaborative', 'content_based', 'hybrid', 'vector_similarity'
    confidence_score FLOAT,
    reason TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    position INT,  -- Position in recommendation list
    
    -- Hybrid recommendation embedding (combines multiple signals)
    recommendation_embedding vector(384),
    
    CONSTRAINT unique_user_resource_rec UNIQUE(user_id, resource_id, generated_at)
);

CREATE INDEX idx_recommendations_user ON recommendations_generated(user_id, generated_at DESC);
CREATE INDEX idx_recommendations_score ON recommendations_generated(user_id, confidence_score DESC);
CREATE INDEX idx_recommendation_embedding ON recommendations_generated 
USING ivfflat (recommendation_embedding vector_cosine_ops) WITH (lists = 100);

-- Recommendation feedback
CREATE TABLE recommendations_feedback (
    feedback_id SERIAL PRIMARY KEY,
    recommendation_id INT UNIQUE REFERENCES recommendations_generated(recommendation_id) ON DELETE CASCADE,
    user_id INT REFERENCES user_id(user_id) ON DELETE CASCADE,
    was_clicked BOOLEAN DEFAULT false,
    was_helpful BOOLEAN,
    feedback_type VARCHAR(50),  -- 'helpful', 'not_helpful', 'irrelevant'
    feedback_text TEXT
);

CREATE INDEX idx_feedback_user ON recommendations_feedback(user_id);

-- ============================================================================
-- HELPER TABLES FOR VECTOR OPERATIONS
-- ============================================================================

-- Query history with query embedding for semantic search caching
CREATE TABLE search_queries (
    query_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES user_id(user_id),
    query_text TEXT NOT NULL,
    query_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    results_count INT,
    
    -- Query embedding for finding similar queries
    query_embedding vector(384)
);

CREATE INDEX idx_query_embedding ON search_queries 
USING ivfflat (query_embedding vector_cosine_ops) WITH (lists = 50);

-- User interaction matrix for collaborative filtering enhancement
CREATE TABLE user_resource_interactions (
    interaction_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES user_id(user_id) ON DELETE CASCADE,
    resource_id INT REFERENCES resources_metadata(resource_id) ON DELETE CASCADE,
    interaction_type VARCHAR(50),  -- 'view', 'download', 'rate', 'favorite'
    interaction_score FLOAT,  -- Weighted score
    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Combined interaction embedding
    interaction_embedding vector(256),
    
    UNIQUE(user_id, resource_id)
);

CREATE INDEX idx_interaction_embedding ON user_resource_interactions 
USING ivfflat (interaction_embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for getting user's complete vector profile
CREATE VIEW user_vector_profile AS
SELECT 
    u.user_id,
    u.email,
    up.profile_embedding,
    upref.preference_embedding,
    up.bio,
    upref.learning_style,
    upref.difficulty_level
FROM user_id u
LEFT JOIN users_profile up ON u.user_id = up.user_id
LEFT JOIN users_preferences upref ON u.user_id = upref.user_id;

-- View for resource complete embeddings
CREATE VIEW resource_vector_profile AS
SELECT 
    rm.resource_id,
    rm.title,
    rm.description,
    rm.resource_type,
    rm.difficulty_level,
    rm.metadata_embedding,
    rc.content_embedding,
    rc.text_embedding,
    rs.view_count,
    rs.average_rating
FROM resources_metadata rm
LEFT JOIN resources_content rc ON rm.resource_id = rc.resource_id
LEFT JOIN resources_stats rs ON rm.resource_id = rs.resource_id;

-- ============================================================================
-- FUNCTIONS FOR VECTOR OPERATIONS
-- ============================================================================

-- Function to find similar resources
CREATE OR REPLACE FUNCTION find_similar_resources(
    query_embedding vector(384),
    limit_count INT DEFAULT 10,
    min_similarity FLOAT DEFAULT 0.7
)
RETURNS TABLE (
    resource_id INT,
    title VARCHAR,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        rm.resource_id,
        rm.title,
        1 - (rm.metadata_embedding <=> query_embedding) AS similarity
    FROM resources_metadata rm
    WHERE 1 - (rm.metadata_embedding <=> query_embedding) >= min_similarity
    ORDER BY rm.metadata_embedding <=> query_embedding
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to find similar users
CREATE OR REPLACE FUNCTION find_similar_users(
    target_user_id INT,
    limit_count INT DEFAULT 10
)
RETURNS TABLE (
    user_id INT,
    username VARCHAR,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        up2.user_id,
        up2.username,
        1 - (up1.profile_embedding <=> up2.profile_embedding) AS similarity
    FROM users_profile up1
    CROSS JOIN users_profile up2
    WHERE up1.user_id = target_user_id 
        AND up2.user_id != target_user_id
        AND up1.profile_embedding IS NOT NULL
        AND up2.profile_embedding IS NOT NULL
    ORDER BY up1.profile_embedding <=> up2.profile_embedding
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function for hybrid search (combines semantic and keyword search)
CREATE OR REPLACE FUNCTION hybrid_search(
    search_query TEXT,
    query_embedding vector(384),
    limit_count INT DEFAULT 20
)
RETURNS TABLE (
    resource_id INT,
    title VARCHAR,
    description TEXT,
    combined_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        rm.resource_id,
        rm.title,
        rm.description,
        -- Weighted combination of vector similarity and text match
        (0.7 * (1 - (rm.metadata_embedding <=> query_embedding)) +
         0.3 * ts_rank(to_tsvector('english', rm.title || ' ' || COALESCE(rm.description, '')), 
                       plainto_tsquery('english', search_query))) AS combined_score
    FROM resources_metadata rm
    WHERE to_tsvector('english', rm.title || ' ' || COALESCE(rm.description, '')) 
          @@ plainto_tsquery('english', search_query)
       OR (1 - (rm.metadata_embedding <=> query_embedding)) > 0.6
    ORDER BY combined_score DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE users_profile IS 'User profiles with vector embeddings for finding similar users and personalization';
COMMENT ON TABLE resources_metadata IS 'Resource metadata with embeddings for semantic search';
COMMENT ON TABLE resources_chunks IS 'Document chunks for fine-grained semantic search within resources';
COMMENT ON TABLE recommendations_generated IS 'Hybrid recommendations combining collaborative filtering and content-based approaches';
COMMENT ON COLUMN users_profile.profile_embedding IS '384-dim vector from user bio, interests, and behavior patterns';
COMMENT ON COLUMN resources_metadata.metadata_embedding IS '384-dim vector from title and description';
COMMENT ON COLUMN resources_content.content_embedding IS '768-dim vector from full document content';
COMMENT ON COLUMN recommendations_generated.recommendation_embedding IS 'Composite embedding combining user preferences, resource content, and collaborative signals';
