import json
import convert_localization, extractor
from pathlib import Path
import time

def get_tech_tree(save_name):
    localization = convert_localization.get_all_localization()

    t0 = time.time()
    data = extractor.Extractor(save_name, ["country_manager", "technology", "player_manager"])
    data.unquote()
    data = data.data
    print(f"Loaded data in {time.time() - t0} seconds")

    countries_data = data["country_manager"]["database"]
    tech_data = data["technology"]["database"]
    players = data["player_manager"]["database"]
    players = [v["country"] for k, v in players.items()]

    techs = dict()
    for key in tech_data:
        if tech_data[key] == "none":
            continue
        researched = tech_data[key]["acquired_technologies"]["value"]
        for t in researched:
            if t not in techs:
                techs[t] = 1
            else:
                techs[t] += 1

    with open("./common_json/technology/technologies/10_production.json", "r") as file:
        prod_tech = [f'{tech}' for tech in json.load(file)]
    with open("./common_json/technology/technologies/20_military.json", "r") as file:
        mil_tech = [f'{tech}' for tech in json.load(file)]
    with open("./common_json/technology/technologies/30_society.json", "r") as file:
        soc_tech = [f'{tech}' for tech in json.load(file)]

    # Determine which new tech is being researched
    print("Techs in research")
    researching_techs = dict()
    for key in tech_data:
        if "research_technology" in tech_data[key]:
            researching = tech_data[key]["research_technology"]
            if researching not in researching_techs:
                researching_techs[researching] = 1
            else:
                researching_techs[researching] += 1
    print(researching_techs)
    print("Research Frontier")
    frontier = [tech for tech in researching_techs if tech not in techs]
    print(frontier)

    # Who is researching which
    notable_countries = players
    for tech_id in tech_data:
        if "research_technology" not in tech_data[tech_id]:
            continue
        country_id = tech_data[tech_id]["country"]
        researching_tech = tech_data[tech_id]["research_technology"]
        country_tag = countries_data[country_id]["definition"]
        if country_tag not in localization:
            country_name = country_tag
        else:
            country_name = localization[country_tag]
        if researching_tech in frontier or country_id in notable_countries:
            print(f"{tech_id} {country_tag} {country_name} : {researching_tech}")
            his_tech = tech_data[tech_id]["acquired_technologies"]["value"]
            his_prod_tech = [tech for tech in his_tech if tech in prod_tech]
            his_mil_tech = [tech for tech in his_tech if tech in mil_tech]
            his_soc_tech = [tech for tech in his_tech if tech in soc_tech]
            print(f"Number of tech: {len(his_tech)}, {[len(his_prod_tech), len(his_mil_tech), len(his_soc_tech)]}")
            his_missing_tech = [tech for tech in techs if tech not in his_tech]
            print("Missing tech")
            print(len(his_missing_tech), his_missing_tech)
            print("")
