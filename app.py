import streamlit as st
from services.supabase_service import SupabaseService
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent

st.markdown(
    '''
    <style>
    /* Sidebar metade da tela */
    [data-testid="stSidebar"] {
        width: 50vw !important;
        min-width: 50vw !important;
        max-width: 50vw !important;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

supabase_service = SupabaseService(
    st.secrets["supabase"]["url"],
    st.secrets["supabase"]["key"]
)

st.markdown("- Agent Orquestrador - Script para Vídeo com Avatar")

@tool
def search_product(product_name: str) -> str:
    """Busca informações do Produto pelo nome

    Args:
        product_name (str): Nome do produto a ser buscado

    Returns:
        str: Informações do produto encontrado ou mensagem de erro
    """
    product = supabase_service.search_product("product", product_name)
    if product:
        return product
    else:
        return "Produto não encontrado."
    
llm = AzureChatOpenAI(
    azure_endpoint=st.secrets["azure"]["endpoint"],
    api_key=st.secrets["azure"]["api_key"],
    api_version=st.secrets["azure"]["api_version"],
    azure_deployment=st.secrets["azure"]["deployment"],
    temperature=0.7,
)

# --- MENU LATERAL PARA SYSTEM PROMPT ---
default_prompt = supabase_service.get_system_prompt()

if "system_prompt" not in st.session_state:
    st.session_state["system_prompt"] = default_prompt

with st.sidebar:
    st.markdown("## Configuração do Prompt do Sistema")
    st.text_area(
        "Prompt do sistema",    
        height="content",
        value=st.session_state["system_prompt"],
        on_change=lambda: st.session_state["system_prompt"],
        key="system_prompt_textarea",
        label_visibility="visible"
    )

    if st.button("Salvar prompt do sistema"):
        supabase_service.update_system_prompt(st.session_state["system_prompt_textarea"])
        st.session_state["system_prompt"] = st.session_state["system_prompt_textarea"]
        st.session_state["chat_memory"] = []

def system_prompt():
    return st.session_state["system_prompt"]

tools = [search_product]
agent = create_react_agent(llm, tools, prompt=system_prompt())

if st.button("Limpar chat e memória"):
    st.toast('Chat e memória limpos com sucesso.', icon='✅')
    st.session_state["chat_memory"] = []

if "chat_memory" not in st.session_state:
    st.session_state["chat_memory"] = []

for msg in st.session_state["chat_memory"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Digite sua solicitação de roteiro"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state["chat_memory"].append({"role": "user", "content": prompt})

    messages = []
    for msg in st.session_state["chat_memory"]:
        role = "human" if msg["role"] == "user" else "assistant"
        messages.append((role, msg["content"]))

    inputs = {"messages": messages}
    result = agent.invoke(inputs)
    
    if result and "messages" in result:
        resposta = result["messages"][-1].content
    else:
        resposta = "Desculpe, ocorreu um erro. Pode tentar novamente?"

    with st.chat_message("assistant"):
        st.markdown(resposta)
    st.session_state["chat_memory"].append({"role": "assistant", "content": resposta})