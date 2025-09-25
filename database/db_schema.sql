-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS docsflow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE docsflow;

-- Tabla de departamentos
CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Tabla de usuarios
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'operador') NOT NULL DEFAULT 'operador',
    department_id INT NULL,
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,
    failed_attempts INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    blocked_at TIMESTAMP NULL DEFAULT NULL,
    unblocked_at TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Tabla de documentos
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    uploaded_by INT NOT NULL,
    department_id INT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    filepath VARCHAR(512) NOT NULL,
    status ENUM('pending', 'processed', 'error') NOT NULL DEFAULT 'pending',
    processed_at TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Tabla de datos extraídos
CREATE TABLE extracted_tables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    table_index INT NOT NULL,
    content JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Tabla de tokens de recuperación de contraseña
CREATE TABLE password_reset_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Índices útiles
CREATE INDEX idx_documents_uploaded_by ON documents(uploaded_by);
CREATE INDEX idx_documents_department_id ON documents(department_id);
CREATE INDEX idx_extracted_tables_document_id ON extracted_tables(document_id);
CREATE INDEX idx_users_department_id ON users(department_id);

-- Valores iniciales de departamentos
INSERT INTO departments (name) VALUES ('Finanzas'), ('Compras'), ('Talento Humano');

-- Usuario admin inicial (cambia la contraseña luego de la creación)
INSERT INTO users (email, password_hash, role, department_id, is_blocked) VALUES (
    'admin@docsflow.com', '$2b$12$eImiTXuWVxfM37uY4JANjQ==', 'admin', NULL, FALSE
);
-- La contraseña hash es solo de ejemplo, reemplázala por un hash real generado con bcrypt.
