# ML Model Details

## Overview

This project uses three ML models for mental health analysis:

## 1. Sentiment Analysis Model

- **Type**: Text Classification
- **Format**: `.pkl` (scikit-learn)
- **Input**: Raw text (journal entries, chat messages)
- **Output**: Sentiment label (positive, negative, neutral) + confidence score
- **Training Data**: Mental health text corpus
- **Algorithm**: TBD (Logistic Regression / SVM / fine-tuned BERT)

## 2. Stress Detection Model

- **Type**: Regression / Classification
- **Format**: `.pkl` (scikit-learn)
- **Input**: Text features extracted from user input
- **Output**: Stress level (low, moderate, high) + numeric score
- **Training Data**: Stress detection dataset
- **Algorithm**: TBD

## 3. Emotion Detection Model

- **Type**: Multi-class Classification
- **Format**: `.h5` (TensorFlow/Keras)
- **Input**: Text or image data
- **Output**: Emotion label + confidence scores for all classes
- **Classes**: anger, disgust, fear, happiness, sadness, surprise, neutral
- **Training Data**: Emotion recognition dataset
- **Algorithm**: TBD (CNN / Transformer)

## Training Pipeline

1. **Preprocessing** (`ml/pipelines/preprocess.py`): Data cleaning, normalization, tokenization
2. **Training** (`ml/pipelines/train.py`): Model training with hyperparameter tuning
3. **Evaluation** (`ml/pipelines/evaluate.py`): Metrics computation and report generation

## Inference

The `ml/inference/predict.py` module is used by the backend to get real-time predictions. Models are loaded once at startup and cached in memory.

## Performance Metrics

| Model      | Accuracy | Precision | Recall | F1 Score |
|------------|----------|-----------|--------|----------|
| Sentiment  | TBD      | TBD       | TBD    | TBD      |
| Stress     | TBD      | TBD       | TBD    | TBD      |
| Emotion    | TBD      | TBD       | TBD    | TBD      |
