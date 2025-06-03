import enum
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SAEnum, Identity
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func # For server-side default timestamps

# Define a Base for declarative models
Base = declarative_base()

# Define Enums for status fields to ensure data integrity
class InputGranularityEnum(enum.Enum):
    whole_text = "whole_text"
    paragraph = "paragraph"

class CorrectionStatusEnum(enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class Prompt(Base):
    __tablename__ = "prompts"

    prompt_id = Column(Integer, Identity(always=True), primary_key=True)
    prompt_id_ref = Column(Text, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    text = Column(Text, nullable=False)
    input_granularity = Column(SAEnum(InputGranularityEnum), nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship: A Prompt can be used in many CorrectionSteps
    correction_steps = relationship("CorrectionStep", back_populates="prompt")

    def __repr__(self):
        return f"<Prompt(prompt_id={self.prompt_id}, name='{self.prompt_id_ref}')>"

class Correction(Base):
    __tablename__ = "corrections"

    correction_id = Column(Integer, Identity(always=True), primary_key=True)
    original_text = Column(Text, nullable=False)
    status = Column(SAEnum(CorrectionStatusEnum), default=CorrectionStatusEnum.pending, nullable=False)

    # Relationship: A Correction can have many CorrectionSteps
    steps = relationship("CorrectionStep", back_populates="correction", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Correction(correction_id={self.correction_id}, status='{self.status.value}')>"

class CorrectionStep(Base):
    __tablename__ = "correction_steps"

    correction_step_id = Column(Integer, Identity(always=True), primary_key=True)
    correction_id = Column(Integer, ForeignKey("corrections.correction_id"), nullable=False)
    prompt_id = Column(Integer, ForeignKey("prompts.prompt_id"), nullable=False)
    
    input_text_sent_to_llm = Column(Text, nullable=False)
    original_text_start_char = Column(Integer, nullable=False)
    paragraph_index = Column(Integer, nullable=True) # Null if prompt is 'whole_text'
    
    status = Column(SAEnum(CorrectionStatusEnum), default=CorrectionStatusEnum.pending, nullable=False)
    llm_response = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    correction = relationship("Correction", back_populates="steps")
    prompt = relationship("Prompt", back_populates="correction_steps")
    analysis_results = relationship("AnalysisResult", back_populates="correction_step", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CorrectionStep(correction_step_id={self.correction_step_id}, status='{self.status.value}')>"

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    analysis_result_id = Column(Integer, Identity(always=True), primary_key=True)
    correction_step_id = Column(Integer, ForeignKey("correction_steps.correction_step_id"), nullable=False)
    
    snippet = Column(Text, nullable=False)
    issue = Column(Text, nullable=False)
    revision = Column(Text, nullable=False)
    
    original_text_start_char = Column(Integer, nullable=False)
    original_text_end_char = Column(Integer, nullable=False)

    # Relationship
    correction_step = relationship("CorrectionStep", back_populates="analysis_results")

    def __repr__(self):
        return f"<AnalysisResult(analysis_result_id={self.analysis_result_id}, snippet_from_llm='{self.snippet[:30]}...')>"
