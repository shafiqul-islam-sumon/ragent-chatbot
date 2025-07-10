---
title: RAGent Chatbot
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.36.2
app_file: app.py
pinned: false
license: mit
short_description: A Smart AI chatbot powered by RAG and AGENT
---

## 💬 Ragent Chatbot Preview

![App Preview](figure/thumbnail.png)

# 🤖 Ragent Chatbot

**Ragent Chatbot** is an intelligent **retrieval-augmented agent assistant** powered by LLMs. It combines the power of **RAG (Retrieval-Augmented Generation)** with **agent-based tool reasoning**, allowing it to dynamically respond using retrieved knowledge or external tools depending on the query.

## 🧠 What It Can Do

- Answer user questions by retrieving information from a custom document store
- You can upload any document and then ask the chatbot to retrieve answer of your question.
- Automatically decide when to use tools (like search, calculator, etc.)
- Combine multiple steps of reasoning using the ReAct agent pattern

## 🛠 Features

- 🔎 **Hybrid Search**: Combines vector similarity and BM25 keyword matching for relevant document retrieval
- 🤖 **ReAct Agent**: Uses tool-based reasoning when knowledge retrieval is insufficient
- 💬 **Gradio Chat UI**: Simple and responsive chat interface
- 🧱 **Modular Tools**: Easily extendable with tools like web search, calculator, and custom APIs

## 📦 Stack

- **Frontend:** Gradio
- **Agent Framework:** LangChain (ReAct agent)
- **Vector DB:** Qdrant
- **LLM:** Gemini
- **Embedding Model:** BAAI/bge-large-en-v1.5

## 🔍 Example Queries

Try asking questions like:

1. **"What is LangChain and how is it different from LlamaIndex?"**  
2. **"Who is the CEO of OpenAI and when was the company founded?"**  
3. **"What is 245 * 92?"**  

💡 The chatbot decides whether to use RAG or call tools like calculator or web search automatically!


## 🔗 GitHub Repository

You can explore the full source code, Docker setup, and implementation details on GitHub:

[👉 RAGent Chatbot](https://github.com/shafiqul-islam-sumon/ragent-chatbot)


## 🚀 Try It Live

- Click url to launch the app in Hugging Face: [RAGent Chatbot](https://huggingface.co/spaces/shafiqul1357/ragent-chatbot)