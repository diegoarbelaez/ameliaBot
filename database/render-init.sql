-- BotDO Database Initialization Script for Render.com
-- Este script se puede ejecutar desde el dashboard de Render después de crear la base de datos
-- O se puede ejecutar manualmente conectándose a la base de datos

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Table: admin_users
-- Purpose: Admin users for API authentication
-- ============================================
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Table: users
-- Purpose: Track message senders across platforms
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(50) NOT NULL, -- 'slack', 'whatsapp', 'web'
    platform_user_id VARCHAR(255) NOT NULL, -- User ID from the platform
    display_name VARCHAR(255),
    email VARCHAR(255),
    platform_metadata JSONB, -- Additional platform-specific data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_platform_user UNIQUE (platform, platform_user_id)
);

-- ============================================
-- Table: channels
-- Purpose: Communication channels across platforms
-- ============================================
CREATE TABLE IF NOT EXISTS channels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(50) NOT NULL, -- 'slack', 'whatsapp', 'web'
    channel_id VARCHAR(255) NOT NULL, -- Channel ID from the platform
    channel_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    platform_metadata JSONB, -- Additional platform-specific data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_platform_channel UNIQUE (platform, channel_id)
);

-- ============================================
-- Table: messages (Main Table)
-- Purpose: Unified message storage for all channels
-- ============================================
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id VARCHAR(255) UNIQUE NOT NULL, -- Message ID from the platform
    channel VARCHAR(50) NOT NULL, -- Origin: 'slack', 'whatsapp', 'web'
    direction VARCHAR(20) NOT NULL, -- 'inbound' or 'outbound'
    sender_type VARCHAR(20) NOT NULL, -- 'bot' or 'user'
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    channel_id UUID REFERENCES channels(id) ON DELETE SET NULL,
    message_text TEXT,
    timestamp TIMESTAMP NOT NULL, -- Original message timestamp
    platform_metadata JSONB, -- Platform-specific data (thread_ts, message_type, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Indexes for Performance
-- ============================================

-- Admin Users indexes
CREATE INDEX IF NOT EXISTS idx_admin_users_username ON admin_users(username);
CREATE INDEX IF NOT EXISTS idx_admin_users_email ON admin_users(email);
CREATE INDEX IF NOT EXISTS idx_admin_users_is_active ON admin_users(is_active);

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_platform ON users(platform);
CREATE INDEX IF NOT EXISTS idx_users_platform_user_id ON users(platform, platform_user_id);
CREATE INDEX IF NOT EXISTS idx_users_display_name ON users(display_name);

-- Channels indexes
CREATE INDEX IF NOT EXISTS idx_channels_platform ON channels(platform);
CREATE INDEX IF NOT EXISTS idx_channels_platform_channel_id ON channels(platform, channel_id);
CREATE INDEX IF NOT EXISTS idx_channels_is_active ON channels(is_active);

-- Messages indexes
CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel);
CREATE INDEX IF NOT EXISTS idx_messages_direction ON messages(direction);
CREATE INDEX IF NOT EXISTS idx_messages_sender_type ON messages(sender_type);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_channel_id ON messages(channel_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- ============================================
-- Triggers for updated_at Timestamps
-- ============================================

-- Function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for all tables
DROP TRIGGER IF EXISTS update_admin_users_updated_at ON admin_users;
CREATE TRIGGER update_admin_users_updated_at 
    BEFORE UPDATE ON admin_users
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_channels_updated_at ON channels;
CREATE TRIGGER update_channels_updated_at 
    BEFORE UPDATE ON channels
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_messages_updated_at ON messages;
CREATE TRIGGER update_messages_updated_at 
    BEFORE UPDATE ON messages
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

