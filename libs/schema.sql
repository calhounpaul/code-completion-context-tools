-- Schema for code analysis database

-- Table for analysis results
CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_md5 TEXT NOT NULL,
    modified_date TEXT NOT NULL,
    analysis_date TEXT NOT NULL,
    analysis_type TEXT NOT NULL,
    parameters TEXT NOT NULL,  -- JSON string of parameters
    output_path TEXT NOT NULL,
    characters_saved INTEGER NOT NULL,
    percent_saved REAL NOT NULL
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_file_path ON analysis_results(file_path);
CREATE INDEX IF NOT EXISTS idx_analysis_type ON analysis_results(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analysis_date ON analysis_results(analysis_date);

-- Table for storing file metadata history (for tracking changes over time)
CREATE TABLE IF NOT EXISTS file_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_md5 TEXT NOT NULL,
    recorded_date TEXT NOT NULL,
    UNIQUE(file_path, file_md5)
);

-- View for summary statistics
CREATE VIEW IF NOT EXISTS analysis_summary AS
SELECT 
    analysis_type,
    COUNT(*) as total_analyses,
    SUM(characters_saved) as total_chars_saved,
    AVG(percent_saved) as avg_percent_saved,
    MAX(percent_saved) as max_percent_saved,
    MIN(percent_saved) as min_percent_saved
FROM analysis_results
GROUP BY analysis_type;