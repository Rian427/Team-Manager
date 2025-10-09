CREATE DATABASE IF NOT EXISTS teammanager CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE teammanager;

CREATE TABLE IF NOT EXISTS positions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  level INT NOT NULL,
  UNIQUE (nome)
);

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  username VARCHAR(80) NOT NULL UNIQUE,
  date_birth DATE,
  position_id INT NOT NULL,
  password VARCHAR(255) NOT NULL,
  FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

INSERT IGNORE INTO positions (name, level) VALUES
  ('CEO', 1),
  ('Gerente', 2),
  ('Analista', 3),
  ('Estagiario', 4);

INSERT IGNORE INTO users (name, username, date_birth, position_id, password)
SELECT 'Lucas Goulart', 'ceo', '1980-01-01', p.id, 'admin'
FROM positions p WHERE p.name = 'CEO'
ON DUPLICATE KEY UPDATE username = username;