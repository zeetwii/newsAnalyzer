from gnews import GNews # needed for google news api
from newspaper import Article # needed for article scraping
from googlenewsdecoder import gnewsdecoder # needed for decoding google news api

import yaml # needed for reading yaml config file
import json # needed for reading json objects from the llm
import os # needed for folder creation

from geopy.geocoders import Nominatim # needed for geolocation

from ollama import chat # needed for LLM
from ollama import ChatResponse # needed for LLM

import time # needed for timestamping

# Only needed for testing
import random # needed for random number generation

# load config settings
with open("./configs/context.yaml", "r") as ymlfile:
    context = yaml.safe_load(ymlfile)

# Configure the LLM settings
model_id = context["llm"]["ID"]
modelContext = context["llm"]["CONTEXT"]
modelJSON = [] # list to hold the JSON output of the LLM

# Create the incidents folder if it doesn't exist
if not os.path.exists("./incidents"):
    os.makedirs("./incidents")


# Configure the geolocation object
geolocator = Nominatim(user_agent="newsAnalyzer")

# Configure the Google News object
googleNews = GNews(language=context["news"]["LANGUAGE"], country=context["news"]["COUNTRY"], period=context["news"]["LOOKBACK"])

# gets all drone stories from the past hour as a json list
newsJSON = googleNews.get_news(context["news"]["TOPIC"])

random.shuffle(newsJSON) # shuffle the list to get a random article for testing

print(f'Found {str(len(newsJSON))} stories')

for story in newsJSON:
    #print(f"\nTitle: {story['title']} \nDate: {str(story['published date'])} \nDescription: {story['description']}")
    #print("\n")
    #print(f"URL: {story['url']}")

    # Adding in try except block to handle errors from URL grabbing

    try:
        # decode the URL to get the actual article
        decodedURL = gnewsdecoder(story['url'], 5)
        article = Article(decodedURL["decoded_url"])
        article.download()
        article.parse()

        #print(f"Article: {article.title}")
        #print(f"Article text: {article.text}")

        messages = [
        {"role": "system", "content": modelContext},
        {"role": "user", "content": f"Analyze the following article: {article.title} /n {article.text}"},
        ]

        response: ChatResponse = chat(model_id, messages)

        #print(response.message.content)

        decision = json.loads(response.message.content)
        print(decision)
        if decision['isIncident'] == True and decision['confidence'] > 0.8:
            #print("Incident detected with high confidence")

            # get the location of the incident
            location = geolocator.geocode(decision['location'])

            # make the JSON object representing the incident
            incident = {
                "title": story['title'],
                "summery": story['description'],
                "date": story['published date'],
                "url": decodedURL["decoded_url"],
                "latitude": location.latitude,
                "longitude": location.longitude
            }

            filePath = f"./incidents/{str(time.time())}.json"

            with open(filePath, "w") as file:
                json.dump(incident, file)

            print(f"Incident detected at {location.latitude}, {location.longitude}")

        else:
            #print(f"Title: {str(article.title)}")
            print("No incident detected")
    except KeyboardInterrupt:
        print("Keyboard interrupt detected, exiting")
        break
    except:
        print("Error processing URL, could be timeout or other issue")