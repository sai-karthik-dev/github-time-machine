import logging

from openai import OpenAI

from app.core.config import CHAT_MAX_TOKENS, CHAT_MODEL, CHAT_TEMPERATURE

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert software architect analyzing a GitHub repository.
Answer questions about the codebase based on the provided context (file contents and commit history).
Be concise, technical, and specific. If the context doesn't contain enough information,
say so honestly rather than guessing."""


class ChatService:
    def __init__(self, supabase, repository_id: str):
        self.supabase = supabase
        self.repository_id = repository_id
        self._client = OpenAI()

    def answer(self, question: str) -> str:
        context = self._fetch_context()
        messages = self._build_messages(question, context)
        return self._call_openai(messages)

    def _fetch_context(self) -> str:
        parts = []

        repo = (
            self.supabase.table("repositories")
            .select("name, owner, language")
            .eq("id", self.repository_id)
            .execute()
        )
        if repo.data:
            r = repo.data[0]
            parts.append(f"Repository: {r.get('owner')}/{r.get('name')} ({r.get('language', 'unknown')})")

        files = (
            self.supabase.table("files")
            .select("file_path, language, size")
            .eq("repository_id", self.repository_id)
            .order("size", desc=True)
            .limit(40)
            .execute()
        )
        if files.data:
            lines = ["\nKey files (top 40 by size):"]
            for f in files.data:
                lines.append(f"  {f['file_path']} ({f.get('language','?')}, {f.get('size',0)} bytes)")
            parts.append("\n".join(lines))

        commits = (
            self.supabase.table("commits")
            .select("message, author, commit_date")
            .eq("repository_id", self.repository_id)
            .order("commit_date", desc=True)
            .limit(20)
            .execute()
        )
        if commits.data:
            lines = ["\nRecent commits (last 20):"]
            for c in commits.data:
                msg = (c.get("message") or "")[:120]
                author = c.get("author") or "unknown"
                lines.append(f"  [{author}] {msg}")
            parts.append("\n".join(lines))

        return "\n".join(parts) if parts else "No repository data available."

    def _build_messages(self, question: str, context: str) -> list[dict]:
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ]

    def _call_openai(self, messages: list[dict]) -> str:
        try:
            response = self._client.chat.completions.create(
                model=CHAT_MODEL,
                messages=messages,
                max_tokens=CHAT_MAX_TOKENS,
                temperature=CHAT_TEMPERATURE,
            )
            return response.choices[0].message.content or ""
        except Exception:
            logger.exception("OpenAI chat failed")
            return "Sorry, I couldn't process that question. The AI service returned an error."
