import requests
import logging 
import torch
import json
import torch.nn.functional as F
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPT2Model


NEWS_API_URL = "https://newsapi.org/v2/everything"
API_KEY = "514ed649b07447da8b4c03a92f96c723"
ARTICLE_COUNT = 10
HEADLINE_COUNT = 5

logging.basicConfig(
    filename= "news_article_headlines.log",
    level=logging.INFO, 
    format= "%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
gen_model = GPT2LMHeadModel.from_pretrained("gpt2")
emb_model = GPT2Model.from_pretrained("gpt2")

tokenizer.pad_token = tokenizer.eos_token
gen_model.pad_token_id = gen_model.config.eos_token_id
emb_model.pad_token_id = emb_model.config.eos_token_id


def get_mean_embedding(input_text):
    input_text_tokens = tokenizer(input_text, return_tensors="pt")
    with torch.no_grad():
        embeddings = emb_model(**input_text_tokens)
    return embeddings.last_hidden_state.mean(dim=1)


def fetch_news_articles(api_key, count) -> list[dict]:
    logger.info ("Fetching new articles.... Please wait")
    news_api_response =  requests.get(NEWS_API_URL, params={
        "apiKey" : api_key,
        "q" : "bitcoin",
        "pageSize" : count
    })

    news_api_response.raise_for_status()
    news_articles = news_api_response.json().get("articles", [])
    logger.info (f"Fetched {len(news_articles)} articles")
    return news_articles


def generate_headlines(prompt):
    news_headline_tokens = tokenizer(prompt, return_tensors="pt").input_ids
    headlines = gen_model.generate(
        news_headline_tokens,
        num_return_sequences=HEADLINE_COUNT,
        do_sample=True,
        max_new_tokens=50,
        temperature=0.8,
        top_k=50,
        top_p=0.95,
    )
    
    return [tokenizer.decode(headline, skip_special_tokens = True).replace(prompt, "").strip() for headline in headlines]



def process_news_articles(news_articles):
    output = {
        "status": "ok",
        "totalResults": len(news_articles),
        "articles": []
    }
    # Get Each News Article and get the Top 5 (count) Headlines
    for id, news_article in enumerate(news_articles):
        
        content = news_article.get("content") or ""
        title = news_article.get("title") or ""
        description = news_article.get("description") or ""

        news_text = f"{title}. {description}. {content}".strip()

        if not news_text:
            continue

        # Prepare Prompt : Get Headline for Each Article (You are in for loop)
        prompt = f"Generate a headline for this news: \n {news_text} \n Headline:"
        headline_candidates = generate_headlines(prompt) # For a Article

        # Get the Original Prompt Embeddings
        news_text_embedding = get_mean_embedding(prompt)

        results = []
        for headline in headline_candidates:
            headline_mean_embedding =  get_mean_embedding(headline)
            score = F.cosine_similarity(headline_mean_embedding,news_text_embedding).item()
            results.append((headline, score))

        results.sort(key=lambda x: x[1], reverse=True)

        top_five_headlines = results[:5]
        
        print ("\n Top 5 Headlines are:\n")
        for i, (headline,similarity)  in enumerate(top_five_headlines,1):
            print (f"{i} - {headline} - Score {similarity:.4f}")

        headlines_to_json = [{"score": headline[1], "text": headline[0]} for headline in top_five_headlines]
        # print(headlines_to_json)

        article_json = {
            "source": news_article.get("source"),
            "author": news_article.get("author"),
            "title": title,
            "description": description,
            "url": news_article.get("url"),
            "urlToImage": news_article.get("urlToImage"),
            "publishedAt": news_article.get("publishedAt"),
            "content": content,
            "headlines": headlines_to_json
        }

        output["articles"].append(article_json)

        with open("generated_top_five_headlines.json", "w") as f:
            json.dump(output, f, indent=4)



if __name__ == "__main__":
    try:
        # Get the News Articles from the News API
        articles = fetch_news_articles(API_KEY, ARTICLE_COUNT) # Get top 5 Articles
        # Process Articles from New API
        process_news_articles (articles)
    except Exception as e:
        logger.info(str(e))
    