-- Supabase setup for MUI Patterns MCP Server
-- Run this in your Supabase SQL editor

-- Create mui_patterns table
CREATE TABLE IF NOT EXISTS mui_patterns (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    component TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    patterns JSONB,
    examples JSONB,
    best_practices JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_mui_patterns_component ON mui_patterns(component);
CREATE INDEX IF NOT EXISTS idx_mui_patterns_timestamp ON mui_patterns(timestamp);

-- Create RLS policies
ALTER TABLE mui_patterns ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "Allow public read access" ON mui_patterns
    FOR SELECT USING (true);

-- Allow authenticated users to insert
CREATE POLICY "Allow authenticated insert" ON mui_patterns
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Create function to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
CREATE TRIGGER update_mui_patterns_updated_at 
    BEFORE UPDATE ON mui_patterns 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data
INSERT INTO mui_patterns (component, patterns, examples, best_practices) VALUES
('chat', 
 '[{"type": "chat_interface", "description": "Material-UI chat interface pattern", "components": ["Card", "TextField", "IconButton", "Avatar"], "layout": "vertical_stack"}]',
 '[{"component": "TextField", "code": "<TextField label=\"Message\" variant=\"outlined\" multiline rows={2} />", "description": "Chat input field"}]',
 '[{"category": "accessibility", "practice": "Use proper ARIA labels", "description": "Ensure chat messages have proper accessibility labels"}]'
),
('dashboard',
 '[{"type": "dashboard_layout", "description": "Material-UI dashboard pattern", "components": ["AppBar", "Drawer", "Grid", "Card"], "layout": "responsive_grid"}]',
 '[{"component": "Card", "code": "<Card sx={{ p: 2 }}><CardContent>Dashboard content</CardContent></Card>", "description": "Dashboard card component"}]',
 '[{"category": "responsive", "practice": "Use Grid system", "description": "Implement responsive layouts with Material-UI Grid"}]'
);

-- Create view for latest patterns
CREATE OR REPLACE VIEW latest_mui_patterns AS
SELECT 
    component,
    patterns,
    examples,
    best_practices,
    timestamp,
    created_at
FROM mui_patterns
WHERE timestamp >= NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC;
