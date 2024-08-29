import configparser
from supabase import create_client, Client

config = configparser.ConfigParser()
config.read('config.ini')

baseUrl = "http://api.steampowered.com/"
supabaseUrl = config['credentials']['supabaseUrl']
supabaseKey = config['credentials']['supabaseKey']
supabase: Client = create_client(supabaseUrl,supabaseKey)