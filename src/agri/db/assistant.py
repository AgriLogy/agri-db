"""SQLAlchemy mirrors of the assistant tables.

Absorbed from agri-api's out-of-band boot script
``back/scripts/ensure_assistant_tables.py`` (Django ``apps.assistant.models``:
``AssistantConversation`` / ``ProactiveNotice``). Byte-matches the live droplet
schema: ``user_id`` is an ORM-level relation in agri-api (Django
``db_constraint=False``) so there are NO DB-level foreign keys, and no DB
defaults.

Note: the current Django ``AssistantConversation`` model declares a
``(user, -updated_at)`` index that does NOT exist on the live table (the
ensure script only creates missing tables, never alters existing ones), so it
is intentionally not modeled here — the schema-of-record matches reality.
"""

from __future__ import annotations

import datetime
import re
from typing import Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Computed,
    Date,
    DateTime,
    Identity,
    Index,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from agri.db.base import AgriBase


class AssistantConversation(AgriBase):
    """One assistant conversation per row, messages stored as a JSON list.

    ``client_id`` is the frontend-generated id, so a conversation keeps a
    stable identity whether first created offline (localStorage) or on the
    server — sync upserts by (user, client_id).
    """

    __tablename__ = "assistant_conversation"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="assistant_conversation_pkey"),
        UniqueConstraint("user_id", "client_id", name="uniq_user_client_conversation"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # Frontend-generated conversation id (stable across devices/offline).
    client_id: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    # [{id, role, content, card?, timestamp}, ...]
    messages: Mapped[list] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )


class AssistantProactiveNotice(AgriBase):
    """Dedup ledger for the proactive-insight scan — one row per user holding
    the last time a proactive notification was pushed (cooldown window)."""

    __tablename__ = "assistant_proactive_notice"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="assistant_proactive_notice_pkey"),
        UniqueConstraint("user_id", name="assistant_proactive_notice_user_id_key"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    last_sent: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


# ---------------------------------------------------------------------------
# Knowledge base (agri-api #461 phase 2)
# ---------------------------------------------------------------------------

#: Lifecycle of an article. Only ``approved`` articles reach the assistant.
KNOWLEDGE_STATUSES = ("draft", "review", "approved", "archived")

#: Subjects the knowledge base covers (the #461 list).
KNOWLEDGE_TOPICS = (
    "irrigation",
    "crops",
    "soil",
    "nutrition",
    "weather",
    "crop_problems",
    "equipment",
    "other",
)

#: Article languages: Moroccan Darija, Modern Standard Arabic, French, English.
KNOWLEDGE_LANGUAGES = ("ary", "ar", "fr", "en")

# Arabic spelling variants folded before indexing AND before querying, so
# "أرض" / "ارض" or "سقية" / "سقيه" match each other: hamza-carrying alefs and
# alef wasla -> bare alef, alef maqsura -> yeh, teh marbuta -> heh. Harakat,
# superscript alef and tatweel (the trailing characters with no counterpart in
# ARABIC_FOLD_TO) are deleted, as SQL translate() does. The Postgres
# ``simple`` config has no Arabic/Darija stemmer, so this folding plus the
# article's ``keywords`` (synonyms, Arabizi spellings) is what makes search
# work across the ways farmers write.
ARABIC_FOLD_FROM = (
    "\u0623\u0625\u0622\u0671\u0649\u0629"
    "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670\u0640"
)
ARABIC_FOLD_TO = "\u0627\u0627\u0627\u0627\u064a\u0647"

_FOLD_TABLE = {
    ord(src): (ARABIC_FOLD_TO[i] if i < len(ARABIC_FOLD_TO) else None)
    for i, src in enumerate(ARABIC_FOLD_FROM)
}


# The definite article is glued to the word, often behind a clitic: الأرض,
# للزيتون, بالتنقيط, فالصيف, والما. Prefix search ("زيتون:*") cannot see past
# it, so a word-initial [و ف ب ك]? + ال/لل is dropped. Same regex in SQL
# (regexp_replace, ARE syntax) and Python (re), with literal characters.
_ARABIC_BLOCK = "\u0600-\u06ff"
_CLITICS = "\u0648\u0641\u0628\u0643"  # wa, fa, bi, ka
_ARTICLES = "\u0627\u0644|\u0644\u0644"  # al, li-l
ARABIC_ARTICLE_RE = f"(^|[^{_ARABIC_BLOCK}0-9a-z])[{_CLITICS}]?({_ARTICLES})"
_ARTICLE = re.compile(ARABIC_ARTICLE_RE)


def fold_arabic(text: str) -> str:
    """Python twin of the SQL normalisation in ``search_vector``: lower-case,
    fold letter variants, drop harakat/tatweel and the glued article. Apply it
    to a query before building the tsquery."""
    return _ARTICLE.sub(r"\1", text.lower().translate(_FOLD_TABLE))


def _folded(column: str) -> str:
    folded = (
        f"translate(lower(COALESCE({column}, ''::text)), "
        f"'{ARABIC_FOLD_FROM}'::text, '{ARABIC_FOLD_TO}'::text)"
    )
    return (
        f"regexp_replace({folded}, '{ARABIC_ARTICLE_RE}'::text, '\\1'::text, 'g'::text)"
    )


#: Generated tsvector: title and keywords weigh A, the body C.
KNOWLEDGE_SEARCH_VECTOR_SQL = (
    f"(setweight(to_tsvector('simple'::regconfig, {_folded('title')}), 'A'::\"char\") || "
    f"setweight(to_tsvector('simple'::regconfig, {_folded('keywords')}), 'A'::\"char\")) || "
    f"setweight(to_tsvector('simple'::regconfig, {_folded('body')}), 'C'::\"char\")"
)


class AssistantKnowledgeArticle(AgriBase):
    """One agricultural knowledge article the assistant may cite.

    Written and approved by staff in agri-admin. ``sources`` is
    ``[{"title": str, "url": str}]``; ``crops`` a list of crop names (empty =
    any crop). ``review_due`` is when the content must be re-checked; an
    approved article past it is still served but flagged as due for review.
    ``*_by_id`` point at ``CustomUser_customuser.id`` (ORM-level, no FK, like
    the other assistant tables).
    """

    __tablename__ = "assistant_knowledge_article"
    __table_args__ = (
        CheckConstraint(
            "status::text = ANY (ARRAY['draft'::character varying, "
            "'review'::character varying, 'approved'::character varying, "
            "'archived'::character varying]::text[])",
            name="assistant_knowledge_article_status_check",
        ),
        CheckConstraint(
            "language::text = ANY (ARRAY['ary'::character varying, "
            "'ar'::character varying, 'fr'::character varying, "
            "'en'::character varying]::text[])",
            name="assistant_knowledge_article_language_check",
        ),
        PrimaryKeyConstraint("id", name="assistant_knowledge_article_pkey"),
        Index(
            "assistant_knowledge_article_search_idx",
            "search_vector",
            postgresql_using="gin",
        ),
        Index("assistant_knowledge_article_status_topic_idx", "status", "topic"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    language: Mapped[str] = mapped_column(String(8), nullable=False)
    topic: Mapped[str] = mapped_column(String(32), nullable=False)
    crops: Mapped[list] = mapped_column(JSONB, nullable=False)
    # Synonyms and spellings the body may not contain (Darija in Arabic script
    # and in Arabizi, French technical words): searched with title weight.
    keywords: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[list] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    review_due: Mapped[Optional[datetime.date]] = mapped_column(Date)
    reviewed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    reviewed_by_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_by_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    updated_by_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    search_vector: Mapped[Optional[str]] = mapped_column(
        TSVECTOR, Computed(KNOWLEDGE_SEARCH_VECTOR_SQL, persisted=True)
    )
