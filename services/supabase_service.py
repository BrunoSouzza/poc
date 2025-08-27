import requests
import streamlit as st

class SupabaseService:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key

    def search_product(self, table_name, product_name):
        headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/vnd.pgrst.object+json"
        }
        params = {
            "name": f"ilike.*{product_name}*",
            "limit": 1
        }
        response = requests.get(f"{self.api_url}/{table_name}", headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data
            else:
                return None
        else:
            st.error(f"Erro na busca: {response.status_code} | {response.text}")
            return None

    def get_system_prompt(self):
        headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/vnd.pgrst.object+json"
        }
        params = {
            "key": "ilike.*system*",
            "limit": 1
        }
        response = requests.get(f"{self.api_url}/keyvalue", headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data["value"]
            else:
                return None
        else:
            st.error(f"Erro na busca: {response.status_code} | {response.text}")
            return None
        
    def update_system_prompt(self, new_prompt):
        headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        params = {
            "key": "eq.system"
        }
        data = {
            "value": new_prompt
        }
        response = requests.patch(f"{self.api_url}/keyvalue", headers=headers, params=params, json=data)
        if response.status_code in [200, 204]:
            st.toast('Prompt do sistema atualizado com sucesso.', icon='✅')
        else:
            st.toast('Erro ao atualizar o prompt do sistema.', icon='❌')
