-- =============================================================
-- FAIR CRM - DATABASE SCHEMA v0.3 (MySQL)
-- =============================================================
-- Database/table/column names are English.
-- Frontend labels/messages can stay Turkish.
-- This is intended for a clean database reset.
-- =============================================================

DROP DATABASE IF EXISTS fair_crm;
CREATE DATABASE fair_crm
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_turkish_ci;

USE fair_crm;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'admin',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_role (role)
);

CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    normalized_company_name VARCHAR(255),
    website VARCHAR(255),
    normalized_website VARCHAR(255),
    main_phone VARCHAR(50),
    normalized_main_phone VARCHAR(50),
    tax_number VARCHAR(50),
    tax_office VARCHAR(100),
    country VARCHAR(100),
    city VARCHAR(100),
    district VARCHAR(100),
    address TEXT,
    description TEXT,
    source VARCHAR(30) NOT NULL DEFAULT 'manual',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    INDEX idx_customers_company_name (company_name(191)),
    INDEX idx_customers_normalized_company_name (normalized_company_name(191)),
    INDEX idx_customers_website (website(191)),
    INDEX idx_customers_normalized_website (normalized_website(191)),
    INDEX idx_customers_main_phone (main_phone),
    INDEX idx_customers_normalized_main_phone (normalized_main_phone),
    INDEX idx_customers_tax_number (tax_number)
);

CREATE TABLE fairs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fair_name VARCHAR(255) NOT NULL,
    normalized_fair_name VARCHAR(255),
    organizer VARCHAR(255),
    venue VARCHAR(255),
    city VARCHAR(100),
    country VARCHAR(100),
    start_date DATE,
    end_date DATE,
    website VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    INDEX idx_fairs_fair_name (fair_name(191)),
    INDEX idx_fairs_normalized_fair_name (normalized_fair_name(191)),
    INDEX idx_fairs_dates (start_date, end_date)
);

CREATE TABLE contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    normalized_full_name VARCHAR(150),
    title VARCHAR(100),
    department VARCHAR(100),
    phone VARCHAR(50),
    email VARCHAR(150),
    note TEXT,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    INDEX idx_contacts_customer_id (customer_id),
    INDEX idx_contacts_full_name (full_name),
    INDEX idx_contacts_normalized_full_name (normalized_full_name)
);

CREATE TABLE customer_phones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    contact_id INT NULL,
    phone_number VARCHAR(50) NOT NULL,
    normalized_phone VARCHAR(50),
    phone_type VARCHAR(50),
    label VARCHAR(50),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    source VARCHAR(30) NOT NULL DEFAULT 'manual',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
    INDEX idx_customer_phones_customer_id (customer_id),
    INDEX idx_customer_phones_contact_id (contact_id),
    INDEX idx_customer_phones_normalized_phone (normalized_phone)
);

CREATE TABLE customer_emails (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    contact_id INT NULL,
    email VARCHAR(150) NOT NULL,
    normalized_email VARCHAR(150),
    email_type VARCHAR(50),
    label VARCHAR(50),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    validation_status VARCHAR(30) NOT NULL DEFAULT 'unknown',
    validation_message VARCHAR(255),
    source VARCHAR(30) NOT NULL DEFAULT 'manual',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
    INDEX idx_customer_emails_customer_id (customer_id),
    INDEX idx_customer_emails_contact_id (contact_id),
    INDEX idx_customer_emails_normalized_email (normalized_email),
    INDEX idx_customer_emails_validation_status (validation_status)
);

CREATE TABLE fair_participations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    fair_id INT NOT NULL,
    hall VARCHAR(100),
    stand_number VARCHAR(100),
    exhibitor_profile_url VARCHAR(500),
    external_exhibitor_id VARCHAR(100),
    participation_status VARCHAR(50) NOT NULL DEFAULT 'active',
    source VARCHAR(30) NOT NULL DEFAULT 'manual',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (fair_id) REFERENCES fairs(id) ON DELETE CASCADE,
    UNIQUE KEY unique_customer_fair (customer_id, fair_id),
    INDEX idx_participations_customer_id (customer_id),
    INDEX idx_participations_fair_id (fair_id),
    INDEX idx_participations_external_id (external_exhibitor_id)
);

CREATE TABLE notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    contact_id INT NULL,
    fair_id INT NULL,
    fair_participation_id INT NULL,
    note_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    detail TEXT NOT NULL,
    note_type VARCHAR(50),
    created_by_user_id INT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
    FOREIGN KEY (fair_id) REFERENCES fairs(id) ON DELETE SET NULL,
    FOREIGN KEY (fair_participation_id) REFERENCES fair_participations(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_notes_customer_id (customer_id),
    INDEX idx_notes_contact_id (contact_id),
    INDEX idx_notes_fair_id (fair_id),
    INDEX idx_notes_participation_id (fair_participation_id)
);

CREATE TABLE import_batches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fair_id INT NULL,
    source_type VARCHAR(50) NOT NULL,
    source_name VARCHAR(255),
    original_file_name VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'uploaded',
    total_rows INT NOT NULL DEFAULT 0,
    successful_rows INT NOT NULL DEFAULT 0,
    warning_rows INT NOT NULL DEFAULT 0,
    error_rows INT NOT NULL DEFAULT 0,
    created_by_user_id INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (fair_id) REFERENCES fairs(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE import_rows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    import_batch_id INT NOT NULL,
    row_number INT NOT NULL,
    raw_data_json JSON,
    normalized_data_json JSON,
    detected_customer_id INT NULL,
    detected_fair_participation_id INT NULL,
    match_score DECIMAL(5,2),
    detection_status VARCHAR(50) NOT NULL DEFAULT 'new',
    decision_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    decision_payload_json JSON,
    warning_message TEXT,
    error_message TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (import_batch_id) REFERENCES import_batches(id) ON DELETE CASCADE,
    FOREIGN KEY (detected_customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    FOREIGN KEY (detected_fair_participation_id) REFERENCES fair_participations(id) ON DELETE SET NULL,
    INDEX idx_import_rows_batch_id (import_batch_id),
    INDEX idx_import_rows_detection_status (detection_status),
    INDEX idx_import_rows_decision_status (decision_status)
);

CREATE TABLE scraper_sources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fair_id INT NULL,
    source_name VARCHAR(255) NOT NULL,
    base_url VARCHAR(500) NOT NULL,
    adapter_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (fair_id) REFERENCES fairs(id) ON DELETE SET NULL
);

CREATE TABLE scraper_runs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scraper_source_id INT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'running',
    total_found INT NOT NULL DEFAULT 0,
    output_file_name VARCHAR(255),
    error_message TEXT,
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at DATETIME NULL,
    FOREIGN KEY (scraper_source_id) REFERENCES scraper_sources(id) ON DELETE CASCADE
);

CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_data_json JSON,
    new_data_json JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_audit_entity (entity_type, entity_id),
    INDEX idx_audit_action (action)
);
