"""
ml/scripts/finetune_bert.py
---------------------------
Fine-tune DistilBERT on WELFake or LIAR dataset for fake news detection.

Requirements:
  pip install torch transformers datasets accelerate

Usage:
  python ml/scripts/finetune_bert.py --data ml/data/WELFake_Dataset.csv --epochs 3

After training, the model is saved to ml/saved_models/distilbert_fakenews/
which the backend will load automatically.
"""

import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

OUTPUT_DIR = Path(__file__).parent.parent / "saved_models" / "distilbert_fakenews"


def finetune(data_path: str, epochs: int = 3, batch_size: int = 16):
    """Full DistilBERT fine-tuning pipeline."""
    try:
        import torch
        from transformers import (
            AutoTokenizer, AutoModelForSequenceClassification,
            TrainingArguments, Trainer, DataCollatorWithPadding,
        )
        import pandas as pd
        from datasets import Dataset
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, f1_score
        import numpy as np
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Run: pip install torch transformers datasets pandas")
        return

    # Load data
    df = pd.read_csv(data_path).dropna(subset=["text"])
    df["combined"] = df["title"].fillna("") + " " + df["text"].fillna("")
    df = df[["combined", "label"]].rename(columns={"combined": "text"})

    train_df, val_df = train_test_split(df, test_size=0.1, random_state=42, stratify=df["label"])

    MODEL_NAME = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, max_length=512)

    train_ds = Dataset.from_pandas(train_df).map(tokenize, batched=True)
    val_ds = Dataset.from_pandas(val_df).map(tokenize, batched=True)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=2,
        id2label={0: "FAKE", 1: "REAL"},
        label2id={"FAKE": 0, "REAL": 1},
    )

    def compute_metrics(pred):
        labels = pred.label_ids
        preds = pred.predictions.argmax(-1)
        return {
            "accuracy": accuracy_score(labels, preds),
            "f1": f1_score(labels, preds, average="weighted"),
        }

    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=32,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_steps=100,
        fp16=torch.cuda.is_available(),
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer),
        compute_metrics=compute_metrics,
    )

    logger.info("🚀 Starting DistilBERT fine-tuning...")
    trainer.train()
    trainer.save_model(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))
    logger.info(f"✅ Model saved → {OUTPUT_DIR}")
    logger.info("Update backend/services/model_service.py to load from this path")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to WELFake CSV")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()
    finetune(args.data, args.epochs, args.batch_size)
