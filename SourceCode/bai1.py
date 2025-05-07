import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# Danh sách trường cần lấy (theo yêu cầu)
desired_fields = [
    'team', 'player', 'nationality', 'position', 'age',
    'games', 'games_starts', 'minutes',
    'goals', 'assists', 'cards_yellow', 'cards_red',
    'xg', 'xg_assist',
    'progressive_carries', 'progressive_passes', 'progressive_passes_received',
    'goals_per90', 'assists_per90', 'xg_per90', 'xg_assist_per90',
    'shots_on_target_pct', 'shots_on_target_per90', 'goals_per_shot', 'average_shot_distance',
    'passes_completed', 'passes_pct', 'passes_progressive_distance',
    'passes_pct_short', 'passes_pct_medium', 'passes_pct_long',
    'passes_into_final_third', 'passes_into_penalty_area', 'crosses_into_penalty_area',
    'progressive_passes',
    'sca', 'sca_per90', 'gca', 'gca_per90',
    'tackles', 'tackles_won',
    'challenge_tackles', 'challenges_lost',
    'blocks', 'blocked_shots', 'blocked_passes', 'interceptions',
    'touches', 'touches_def_pen_area', 'touches_def_3rd', 'touches_mid_3rd', 'touches_att_3rd', 'touches_att_pen_area',
    'take_ons', 'take_ons_won_pct', 'take_ons_tackled_pct',
    'carries', 'carries_progressive_distance', 'carries_into_final_third', 'carries_into_penalty_area', 'miscontrols', 'dispossessed',
    'passes_received', 'progressive_passes_received',
    'fouls', 'fouled', 'offsides', 'crosses', 'ball_recoveries',
    'aerials_won', 'aerials_lost', 'aerials_won_pct',
    # các cột thủ môn
    'GA90', 'Save%', 'CS%', 'PK Save%'
]

# Mapping cho các bảng dữ liệu
stats_mapping = {
    "nationality": "nationality",
    "position": "position",
    "age": "age",
    "games": "games",
    "games_starts": "games_starts",
    "minutes": "minutes",
    "goals": "goals",
    "assists": "assists",
    "cards_yellow": "cards_yellow",
    "cards_red": "cards_red",
    "xg": "xg",
    "xg_assist": "xg_assist",
    "progressive_carries": "progressive_carries",
    "progressive_passes": "progressive_passes",
    "progressive_passes_received": "progressive_passes_received",
    "goals_per90": "goals_per90",
    "assists_per90": "assists_per90",
    "xg_per90": "xg_per90",
    "xg_assist_per90": "xg_assist_per90",
}
keeper_mapping = {
    "gk_goals_against_per90": "GA90",
    "gk_save_pct":            "Save%",
    "gk_clean_sheets_pct":    "CS%",
    "gk_pens_save_pct":       "PK Save%",
}
shooting_mapping = {
    "shots": "shots",
    "shots_on_target": "shots_on_target",
    "shots_on_target_pct": "shots_on_target_pct",
    "shots_per90": "shots_per90",
    "shots_on_target_per90": "shots_on_target_per90",
    "goals_per_shot": "goals_per_shot",
    "goals_per_shot_on_target": "goals_per_shot_on_target",
    "average_shot_distance": "average_shot_distance",
}
passing_mapping = {
    "passes_completed": "passes_completed",
    "passes_pct": "passes_pct",
    "passes_progressive_distance": "passes_progressive_distance",
    "passes_pct_short": "passes_pct_short",
    "passes_pct_medium": "passes_pct_medium",
    "passes_pct_long": "passes_pct_long",
    "passes_into_final_third": "passes_into_final_third",
    "passes_into_penalty_area": "passes_into_penalty_area",
    "crosses_into_penalty_area": "crosses_into_penalty_area",
    "progressive_passes": "progressive_passes",
}
sca_gca_mapping = {
    "sca": "sca",
    "sca_per90": "sca_per90",
    "gca": "gca",
    "gca_per90": "gca_per90",
}
defense_mapping = {
    "tackles": "tackles",
    "tackles_won": "tackles_won",
    "challenge_tackles": "challenge_tackles",
    "challenges_lost": "challenges_lost",
    "blocks": "blocks",
    "blocked_shots": "blocked_shots",
    "blocked_passes": "blocked_passes",
    "interceptions": "interceptions",
}
possession_mapping = {
    "touches": "touches",
    "touches_def_pen_area": "touches_def_pen_area",
    "touches_def_3rd": "touches_def_3rd",
    "touches_mid_3rd": "touches_mid_3rd",
    "touches_att_3rd": "touches_att_3rd",
    "touches_att_pen_area": "touches_att_pen_area",
    "take_ons": "take_ons",
    "take_ons_won_pct": "take_ons_won_pct",
    "take_ons_tackled_pct": "take_ons_tackled_pct",
    "carries": "carries",
    "carries_progressive_distance": "carries_progressive_distance",
    "carries_into_final_third": "carries_into_final_third",
    "carries_into_penalty_area": "carries_into_penalty_area",
    "miscontrols": "miscontrols",
    "dispossessed": "dispossessed",
    "passes_received": "passes_received",
    "progressive_passes_received": "progressive_passes_received",
}
misc_mapping = {
    "fouls": "fouls",
    "fouled": "fouled",
    "offsides": "offsides",
    "crosses": "crosses",
    "ball_recoveries": "ball_recoveries",
    "aerials_won": "aerials_won",
    "aerials_lost": "aerials_lost",
    "aerials_won_pct": "aerials_won_pct",
}

def init_driver():
    opts = Options()
    opts.add_argument('--headless')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--enable-unsafe-swiftshader')
    opts.add_argument('--use-gl=swiftshader')
     # tắt background networking (bao gồm GCM)
    opts.add_argument('--disable-background-networking')
    opts.add_argument('--disable-gcm')
    # tắt log “DevTools listening”  
    opts.add_experimental_option('excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(options=opts)

def get_team_urls(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    table = wait.until(EC.presence_of_element_located((By.ID, "results2024-202591_overall")))
    links = table.find_elements(By.CSS_SELECTOR, "td[data-stat='team'] > a")
    urls = []
    for a in links:
        href = a.get_attribute("href")
        if href.startswith("/"):
            href = "https://fbref.com" + href
        urls.append(href)
        time.sleep(random.uniform(1, 2))
    return urls

def scrape_table(driver, table_id, mapping):
    data = {}
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"table#{table_id} tbody tr"))
        )
    except:
        return data
    table = driver.find_element(By.CSS_SELECTOR, f"table#{table_id}")
    for row in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
        try:
            name = row.find_element(By.CSS_SELECTOR, "th[data-stat='player'] a").text.strip()
        except NoSuchElementException:
            continue
        record = {}
        for ds, key in mapping.items():
            try:
                record[key] = row.find_element(By.CSS_SELECTOR, f"td[data-stat='{ds}']").text.strip()
            except NoSuchElementException:
                record[key] = ''
        data[name] = record
    return data

def main():
    driver = init_driver()
    base_url = 'https://fbref.com/en/comps/9/2024-2025/Premier-League-Stats'
    team_urls = get_team_urls(driver, base_url)
    all_records = []

    for url in team_urls:
        driver.get(url)
        print(f"Scraping {url}...")
        time.sleep(random.uniform(1, 2))
        # chỉ lấy tên đội trước dấu " Stats"
        full = driver.find_element(By.TAG_NAME, 'h1').text.strip()
        team_name = full.split(" Stats")[0]

        keeper_info = scrape_table(driver, 'stats_keeper_9', keeper_mapping)
        shooting_info   = scrape_table(driver, 'stats_shooting_9', shooting_mapping)
        passing_info    = scrape_table(driver, 'stats_passing_9', passing_mapping)
        sca_gca_info    = scrape_table(driver, 'stats_gca_9', sca_gca_mapping)
        defense_info    = scrape_table(driver, 'stats_defense_9', defense_mapping)
        possession_info = scrape_table(driver, 'stats_possession_9', possession_mapping)
        misc_info       = scrape_table(driver, 'stats_misc_9', misc_mapping)
        standard_info   = scrape_table(driver, 'stats_standard_9', stats_mapping)

        for player, std in standard_info.items():
            # skip < 90'
            mp = int(std.get('minutes','0').replace(',','') or 0)
            if mp < 90: continue

            rec = {'team': team_name, 'player': player}
            # nationality lấy phần sau
            nat = std.get('nationality','').split()[-1]
            rec['nationality'] = nat or 'N/a'
            # age lấy trước dấu '-'
            ag = std.get('age','').split('-')[0]
            rec['age'] = ag or 'N/a'

            # add các trường standard
            for k,v in std.items():
                if k not in ('nationality','age'):
                    rec[k] = v

            # khởi default thủ môn
            for col in keeper_mapping.values():
                rec[col] = 'N/a'
            # nếu GK thì cập nhật
            if std.get('position')=='GK' and player in keeper_info:
                rec.update(keeper_info[player])

            # các bảng khác
            if player in shooting_info:   rec.update(shooting_info[player])
            if player in passing_info:    rec.update(passing_info[player])
            if player in sca_gca_info:    rec.update(sca_gca_info[player])
            if player in defense_info:    rec.update(defense_info[player])
            if player in possession_info: rec.update(possession_info[player])
            if player in misc_info:       rec.update(misc_info[player])

            all_records.append(rec)

    driver.quit()

    df = pd.DataFrame(all_records)
    df = df[desired_fields]
    df.fillna('N/a', inplace=True)
    df.replace('', 'N/a', inplace=True)
    df.sort_values(by='player', inplace=True)
    df.to_csv('results.csv', index=False)
    return df

if __name__ == '__main__':
    df = main()
    print(df.head())