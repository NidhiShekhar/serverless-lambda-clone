CREATE TABLE IF NOT EXISTS functions (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    language TEXT NOT NULL,
    code TEXT NOT NULL,
    timeout INT DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS execution_logs (
    id SERIAL PRIMARY KEY,
    function_id INT REFERENCES functions(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    execution_time FLOAT,
    error_log TEXT,
    output TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
