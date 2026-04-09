-- Create database if not exists
CREATE DATABASE IF NOT EXISTS healthcare;
USE healthcare;

-- Drop tables in correct order (if they exist)
DROP TABLE IF EXISTS conversations;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS families;

-- Create families table
CREATE TABLE families (
    id INT AUTO_INCREMENT PRIMARY KEY,
    family_name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create members table
CREATE TABLE members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    family_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    age INT,
    face_encoding LONGBLOB,
    face_image_path VARCHAR(255),
    medical_history TEXT,
    emergency_contact VARCHAR(20),
    last_seen TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    INDEX idx_family (family_id),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create conversations table
CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    message TEXT NOT NULL,
    response TEXT,
    emotion VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
    INDEX idx_member (member_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create face_metrics table for recognition quality tracking
CREATE TABLE face_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    recognition_attempts INT DEFAULT 0,
    successful_recognitions INT DEFAULT 0,
    average_confidence DECIMAL(5,4) DEFAULT 0,
    last_recognition TIMESTAMP NULL,
    face_quality_score DECIMAL(5,2) DEFAULT 0,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
    INDEX idx_member_metrics (member_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert sample data for testing
INSERT INTO families (family_name) VALUES ('Sharma'), ('Patel'), ('Singh');

-- Insert sample members
INSERT INTO members (family_id, name, role, age, medical_history, emergency_contact) VALUES
(1, 'Raj Sharma', 'Father', 45, 'Diabetes Type 2', '9876543210'),
(1, 'Priya Sharma', 'Mother', 40, 'None', '9876543211'),
(1, 'Aarav Sharma', 'Child', 10, 'Asthma', '9876543212'),
(2, 'Anita Patel', 'Grandmother', 70, 'Hypertension, Arthritis', '9876543213'),
(3, 'Amrit Singh', 'Father', 50, 'Heart Condition', '9876543214');