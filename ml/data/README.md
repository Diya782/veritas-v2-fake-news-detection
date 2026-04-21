# ML Data Directory

## Datasets

### WELFake Dataset (Recommended)
- **Source**: Kaggle — search "WELFake dataset"
- **Size**: ~72,000 articles (36k real + 36k fake)
- **Format**: CSV with columns: `title`, `text`, `label` (0=fake, 1=real)
- **Download**: https://www.kaggle.com/datasets/saurabhshahane/fake-news-classification

### LIAR Dataset (For BERT fine-tuning)
- **Source**: https://huggingface.co/datasets/liar
- **Size**: ~12,836 statements with 6-class labels
- **Use case**: Fine-grained credibility classification

### FakeNewsNet
- **Source**: https://github.com/KaiDMML/FakeNewsNet
- **Content**: PolitiFact + GossipCop with social context

## Setup

1. Download WELFake CSV
2. Place as: `ml/data/WELFake_Dataset.csv`
3. Run training:
   ```
   python ml/scripts/train.py --data ml/data/WELFake_Dataset.csv
   ```

The model auto-trains on a built-in demo corpus if no dataset is provided,
but real accuracy requires the full dataset (~95% accuracy on WELFake).
