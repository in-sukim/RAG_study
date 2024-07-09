import streamlit as st
from langchain_core.messages.chat import ChatMessage
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_teddynote.prompts import load_prompt
from langchain import hub
from dotenv import load_dotenv


st.title("나의 첫 Streamlit 앱")
st.markdown("#### 이 앱은 Streamlit으로 구현했습니다.")


# 처음 한번만 실행하기 위한 코드
if "messages" not in st.session_state:
    # 대화기록을 저장하기 위한 용도로 생성한다.
    st.session_state["messages"] = []

# 사이드바 생성
with st.sidebar:
    # 초기화 버튼
    clear_btn = st.button("대화기록 초기화")
    if clear_btn:
        st.session_state["messages"] = []
    selected_prompt = st.selectbox(
        "프롬프트를 선택해주세요.", ("기본모드", "SNS 게시글", "요약"), index=0
    )


# 이전 대화 출력
def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)


print_messages()


# 새로운 메시지 추가
def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


def create_chain(prompt_type):
    # prompt | llm | output_parser
    # prompt 지정
    if prompt_type == "기본모드":
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "당신은 친절한 AI 어시스턴스 입니다. 다음의 질문에 간결하게 답변해주세요. 항상 한국어로 답변해주세요.",
                ),
                ("user", "{question}"),
            ]
        )
    elif prompt_type == "SNS 게시글":
        prompt = load_prompt("./prompts/sns_prompt.yaml")
    elif prompt_type == "요약":
        prompt = hub.pull("teddynote/chain-of-density-map-korean:946ed62d")

    # llm 지정
    llm = ChatOllama(model="llama3", temperature=0)
    # 출력 파서
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser
    return chain


# 사용자의 입력
user_input = st.chat_input("대화를 입력하세요.")

if user_input:
    # 사용자의 입력
    st.chat_message("user").write(user_input)
    chain = create_chain(selected_prompt)
    # 스트리밍 호출
    response = chain.stream({"question": user_input})
    with st.chat_message("assistant"):
        container = st.empty()
        ai_answer = ""
        for token in response:
            ai_answer += token
            container.markdown(ai_answer)
    # st.chat_message("assistant").write(ai_answer)

    # 대화기록 저장.
    add_message("user", user_input)
    add_message("assistant", ai_answer)
    ChatMessage(role="user", content=user_input)
    ChatMessage(role="assistant", content=ai_answer)
