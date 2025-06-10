CREATE DATABASE IF NOT EXISTS feple_analysis;
USE feple_analysis;

DROP TABLE IF EXISTS analysis_results;

CREATE TABLE analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    call_id VARCHAR(20) NOT NULL,
    evaluation_score INT NOT NULL,
    strengths TEXT NOT NULL,
    weaknesses TEXT NOT NULL,
    improvements TEXT NOT NULL,
    coaching_message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_call_id (call_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; 