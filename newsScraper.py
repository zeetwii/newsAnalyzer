from gnews import GNews # needed for google news api
import yaml # needed for reading yaml config file

# load config settings
with open("./configs/context.yaml", "r") as ymlfile:
    context = yaml.safe_load(ymlfile)

# Configure the Google News object
googleNews = GNews(language=context["news"]["LANGUAGE"], country=context["news"]["COUNTRY"], period=context["news"]["LOOKBACK"])

# gets all drone stories from the past hour as a json list
droneJSON = googleNews.get_news(context["news"]["TOPIC"])

print(f'Found {str(len(droneJSON))} stories')

for story in droneJSON:
    print(f"\nTitle: {story['title']} \nDate: {str(story['published date'])} \nDescription: {story['description']}")
    print("\n")