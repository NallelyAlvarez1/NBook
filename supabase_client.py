from supabase import create_client, Client


def initialize_supabase_client(secrets: dict) -> Client:
    try:
        SUPABASE_URL = secrets["supabase"]["url"]
        SUPABASE_KEY = secrets["supabase"]["key"]
    except KeyError as e:
        raise ValueError(f"Falta la clave {e} en la configuración de secretos de Supabase.")

    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase_client
