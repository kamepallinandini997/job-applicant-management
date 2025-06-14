import json
import requests
import logging 
import torch
import torch.nn.functional as F
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPT2Model

NEWS_API_URL = "https://newsapi.org/v2/everything"
API_KEY = "6e69335621364db3ab97992db24408f5"
HEADLINE_COUNT =5  
ARTICLE_COUNT = 1
Q ="bitcoin"

logging.basicConfig(level=logging.INFO, format= "%(asctime)s - %(levelname)s -%(message)s")


tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
gen_model = GPT2LMHeadModel.from_pretrained("gpt2")
emb_model = GPT2Model.from_pretrained("gpt2")

# Add Padding Tokens {Becuase this is not default in GPT2}
tokenizer.pad_token = tokenizer.eos_token

gen_model.pad_token_id = gen_model.config.eos_token_id
emb_model.pad_token_id = emb_model.config.eos_token_id


def get_mean_embedding(input_text):
    input_text_tokens = tokenizer(input_text, return_tensors="pt")
    with torch.no_grad():
        embeddings = emb_model(**input_text_tokens)
    return embeddings.last_hidden_state.mean(dim=1) # Share [1,768] 768-d


def fetch_news_articles(Q: str, api_key: str) -> list[dict]:
    logging.info ("Fetching new articles.... Please wait")
    news_api_response =  requests.get(NEWS_API_URL, params = {
        "apiKey" : api_key,
        "pageSize": ARTICLE_COUNT,
        "q": Q
    })

    news_api_response.raise_for_status()
    news_articles = news_api_response.json().get("articles", [])
    logging.info (f"Fetched {len(news_articles)} articles")
    return news_articles


def generate_headlines(prompt):
    news_headline_tokens = tokenizer(prompt, return_tensors="pt").input_ids
    headlines = gen_model.generate (
        news_headline_tokens,
        num_return_sequences = HEADLINE_COUNT, # Fix the issue for Greedy - Beam message
        max_new_tokens =20,
        temperature = 0.8,
        top_k=50,
        top_p  = 0.95,
        do_sample=True
    )
    return [tokenizer.decode(headline, skip_special_tokens = True).replace(prompt, "").strip() for headline in headlines]



def process_news_articles(news_articles):

    output_data = {
        "status": "ok",
        "totalResults": len(news_articles),
        "articles": []
    }

    # Get Each News Article and get the Top 3 (count) Headlines
    for id, news_article in enumerate(news_articles):
        content = news_article.get("content") or ""
        title = news_article.get("title") or ""
        description = news_article.get("description") or ""

        # News Article =  "title + description + content"
        news_text = f"{title}. {description}. {content}".strip()

        if not news_text: # if Empty them get next article : continue
            continue

        # Prepare Prompt : Get Healine  for Each Article (You are in for loop)
        prompt = f"Write a short, one-line headline for this news: \n {news_text} \n Headline:"
        headline_candidates = generate_headlines(prompt)  or []
        if not headline_candidates:
                continue

        # Get the Original Prompt Embeddings
        news_text_embedding = get_mean_embedding(prompt)

        result = []
        for headline in headline_candidates:
            headline_mean_embedding =  get_mean_embedding(headline)
            score = F.cosine_similarity(headline_mean_embedding,news_text_embedding).item()
            result.append((headline, score)
            )

        # Sort all headlines by score descending
        result.sort(key=lambda x: x[1], reverse=True)

        # Print best one (optional)
        best_headline, score = result[0]
        logging.info(f"Top headline: {best_headline} - Score {score:.4f}")

        # Prepare headlines list for JSON
        headlines_json = [
            {
                "score": round(score_item[1], 4),
                "text": score_item[0]
            }
            for score_item in result
        ]

        output_data["articles"].append({
            "title": title,
            "description": description,
            "content": content,
            "headlines": headlines_json
        })

    # Write the final structured output to a JSON file
    with open("news_output.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    try:
        articles = fetch_news_articles(Q, API_KEY)
        process_news_articles(articles)
    except Exception as e:
        logging.error(f"Error: {str(e)}")
