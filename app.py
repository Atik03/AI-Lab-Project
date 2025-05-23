from flask import Flask, render_template, request
from newspaper import Article, Config
from transformers import pipeline

app = Flask(__name__)

# Set user agent
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
config = Config()
config.browser_user_agent = user_agent
config.request_timeout = 10

# Load the summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text, max_length=130, min_length=30):
    chunks = text.split('. ')
    result = ''
    for i in range(0, len(chunks), 5):
        chunk = '. '.join(chunks[i:i + 5])
        if chunk:
            summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
            result += summary[0]['summary_text'] + ' '
    return result.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        try:
            article = Article(url, config=config)
            article.download()
            article.parse()
            summary = summarize_text(article.text)

            return render_template("index.html",
                                   title=article.title,
                                   author=article.authors,
                                   source=article.source_url,
                                   summary=summary,
                                   url=url)
        except Exception as e:
            return render_template("index.html", error=str(e))
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
