# AI Content Aggregator 🚀

An asynchronous news aggregator that uses artificial intelligence to summarize and analyze the tone of articles.

## 🛠 Technology stack
- **Backend:** FastAPI (Python 3.10+)
- **Database:** PostgreSQL + SQLAlchemy (Async)
- **Task Queue:** Celery + Redis
- **AI/ML:** Hugging Face API (BART model) & NLP sentiment analysis
- **Infrastructure:** Docker & Docker Compose

## ✨ Key Features
- **Async Processing:** Parsing RSS feeds and AI queries do not interfere with API operations.
- **AI Summarization:** Automatically generate a summary of an article using a model `facebook/bart-large-cnn`.
- **Sentiment Analysis:** Each article is assigned a sentiment score (positive/negative)).
- **Smart Search:** Full-text search of articles and filtering by mood.
- **Reliability:** A retry system (Celery Retries) and API rate limiting have been implemented (Semaphores).
