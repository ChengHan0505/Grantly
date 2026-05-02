import os


# Dummy environment variables for testing.
# These prevent import/startup errors when main.py expects API keys.
os.environ.setdefault("ZAI_API_KEY", "test-zai-key")
os.environ.setdefault("GLM_API_KEY", "test-glm-key")
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")

os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-supabase-key")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-supabase-anon-key")

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("ENVIRONMENT", "test")