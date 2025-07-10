import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import gradio as gr
from agent import Agent
from config import Config
from memory.chat_memory import MemoryManager
from utils.html_template import HtmlTemplates
from vector_db.qdrant_db import QdrantDBClient
from langchain_core.messages import HumanMessage, AIMessage


class WebApp:
    def __init__(self):
        self.title = "RAGent Chatbot"
        self.uploaded_files = None
        self.upload_btn = None
        self.progress_output = None
        self.status_output = None
        self.css = HtmlTemplates.css()

        self.agent = Agent()
        self.memory = MemoryManager()
        self.qdrant_client = QdrantDBClient()

    def build_ui(self):
        with gr.Blocks(theme=gr.themes.Default(), css=self.css) as demo:
            self.build_header()
            with gr.Row():
                self.build_upload_section()
                self.build_chat_section()
        return demo

    def build_header(self):
        with gr.Row():
            with gr.Column():
                gr.HTML(f"<h1 id='title'>💬 {self.title}</h1>")

    def clear_outputs(self):
        return "", ""

    def build_upload_section(self):
        with gr.Column(scale=3):
            gr.Markdown("### 📂 Drag & Drop Files Below")
            self.uploaded_files = gr.File(
                file_types=Config.FILE_EXTENSIONS,
                file_count="multiple",
                label="pdf, docx, xlsx, pptx, csv, txt, json"
            )
            self.upload_btn = gr.Button(value="Upload Files", elem_id="upload-btn", icon=Config.UPLOAD_ICON)
            self.progress_output = gr.HTML()
            self.status_output = gr.Markdown()

            self.upload_btn.click(
                fn=self.clear_outputs,
                inputs=[],
                outputs=[self.progress_output, self.status_output]
            ).then(
                fn=self.upload_and_process,
                inputs=self.uploaded_files,
                outputs=[self.progress_output, self.status_output],
                show_progress="hidden"
            )

    def build_chat_section(self):
        with gr.Column(scale=7):
            gr.Markdown("### 🤖 Ask Your Question")
            gr.ChatInterface(
                fn=self.run_agent,
                type="messages",
                show_progress="full",
                save_history=False,
            )

    def run_agent(self, query, history):
        session_id = Config.SESSION_ID

        # Get history
        past_messages = self.memory.get(session_id)

        # Run agent (it appends the user query internally)
        response = self.agent.run(query, past_messages)
        #print("##### response : ", response)

        # convert response to string. If response is a dict like {'input': ..., 'output': ...}
        if isinstance(response, dict) and "output" in response:
            answer = response["output"]
        else:
            answer = str(response)

        # Save user + assistant message to memory
        self.memory.add(session_id, HumanMessage(content=query))
        self.memory.add(session_id, AIMessage(content=answer))

        return f"‍🤖 {answer}"

    def upload_and_process(self, files):
        if not files or len(files) == 0:
            yield HtmlTemplates.error_bar(), ""
            return

        total = len(files)
        failed_files = []

        for i, file in enumerate(files):
            file_path = file.name  # path to temp file

            try:
                # Load, chunk, and insert to vector DB
                file_chunks = self.qdrant_client.load_and_chunk_docs(file_path)
                self.qdrant_client.insert_chunks(file_chunks)

            except Exception as e:
                failed_files.append(file_path)
                yield HtmlTemplates.progress_bar(int((i + 1) / total * 100), i + 1, total), (
                    f"⚠️ Skipped file {i + 1}/{total}: {os.path.basename(file_path)} - {str(e)}"
                )
                continue

            percent = int((i + 1) / total * 100)
            yield HtmlTemplates.progress_bar(percent, i + 1, total), f"📄 Processed {i + 1}/{total} file(s)..."

        success_count = total - len(failed_files)
        final_msg = f"✅ {success_count}/{total} file(s) processed and stored in DB!"

        if failed_files:
            failed_list = "\n".join(f"❌ {os.path.basename(f)}" for f in failed_files)
            final_msg += f"\n\n⚠️ Failed to process:\n{failed_list}"

        yield HtmlTemplates.progress_bar(100, total, total), final_msg

    def upload_and_process1(self, files):
        if not files or len(files) == 0:
            yield HtmlTemplates.error_bar(), ""
            return

        total = len(files)

        for i, file in enumerate(files):
            file_path = file.name  # get file path of temporary folder

            # Load, chunk, and insert to vector DB
            file_chunks = self.qdrant_client.load_and_chunk_docs(file_path)
            self.qdrant_client.insert_chunks(file_chunks)

            percent = int((i + 1) / total * 100)
            yield HtmlTemplates.progress_bar(percent, i + 1, total), f"📄 Processed {i + 1}/{total} file(s)..."

        yield HtmlTemplates.progress_bar(100, total, total), f"✅ {total} file(s) processed and stored in DB!"


if __name__ == "__main__":
    app = WebApp()
    demo = app.build_ui()
    demo.launch()
