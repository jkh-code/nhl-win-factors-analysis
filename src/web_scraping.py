from bs4 import BeautifulSoup
from selenium import webdriver

from pymongo import MongoClient
from pymongo import collection
# import pymongo
import psycopg2 as pg2
from sqlalchemy import create_engine
from os import environ

import pandas as pd
import time

from typing import Union, Type, List, Dict

from sqlalchemy.engine.base import Engine

def get_soup(url: str) -> BeautifulSoup:
    """Return parsed HTML code using Selenium and ChromeDriver."""
    driver = webdriver.Chrome()
    driver.get(url)
    source = driver.page_source
    driver.close()

    soup = BeautifulSoup(source, 'lxml')
    return soup

def make_url(year: int, page: int=0) -> str:
    url = ('http://www.nhl.com/stats/teams?aggregate=0&'
            + f'reportType=game&seasonFrom={year}{year+1}&'
            + f'seasonTo={year}{year+1}&dateFromSeason&gameType=2'
            + f'&filter=gamesPlayed,gte,1&sort=points,wins&page={page}&'
            + 'pageSize=100')
    return url

def convert_double_dash(
        cell: str, 
        type_constructor: Union[Type[int], Type[float]]) -> Union[int, float]:
    if cell == '--':
        return None
    return type_constructor(cell)

def make_postgres_conn(
        dbname: str='postgres', port: int=5432) -> pg2.extensions.connection:
    conn = pg2.connect(
        dbname=dbname,
        port=port,
        host=environ['PG_HOST'],
        user=environ['PG_USER'],
        password=environ['PG_PASSWORD'])
    return conn

def make_alchemy_engine(
        dbname: str='postgres', port: int=5432) -> Engine:
    username = environ['PG_USER']
    password = environ['PG_PASSWORD']
    host = environ['PG_HOST']
    string = f'postgresql://{username}:{password}@{host}:{port}/{dbname}'
    return create_engine(string)

def extract_page_table(
        soup: BeautifulSoup, season: int, 
        page: int, row_schema: dict) -> List[Dict]:
    """Extract NHL data from parsed HTML."""
    rows = soup.find_all('div', class_='rt-tr-group')

    all_rows = []
    for row in rows:
        values = row.find_all('div', class_='rt-td')
        if values[0].text.strip() == '&nbsp;' or values[0].text.strip() == '':
            break

        new_row = row_schema.copy()
        new_row['team'] = values[1].text.strip()
        new_row['game'] = values[2].text.strip()
        new_row['gp'] = int(values[3].text.strip())
        new_row['wins'] = int(values[4].text.strip())
        new_row['losses'] = int(values[5].text.strip())
        new_row['ties'] = convert_double_dash(values[6].text.strip(), int)
        new_row['ot_losses'] = int(values[7].text.strip())
        new_row['points'] = int(values[8].text.strip())
        new_row['point_percent'] = float(values[9].text.strip())
        new_row['reg_wins'] = int(values[10].text.strip())
        new_row['reg_ot_wins'] = int(values[11].text.strip())
        new_row['so_wins'] = int(values[12].text.strip())
        new_row['gf'] = int(values[13].text.strip())
        new_row['ga'] = int(values[14].text.strip())
        new_row['gf_per_gp'] = convert_double_dash(
            values[15].text.strip(), float)
        new_row['ga_per_gp'] = convert_double_dash(
            values[16].text.strip(), float)
        new_row['pp_percent'] = convert_double_dash(
            values[17].text.strip(), float)
        new_row['pk_percent'] = convert_double_dash(
            values[18].text.strip(), float)
        new_row['pp_net_percent'] = convert_double_dash(
            values[19].text.strip(), float)
        new_row['pk_net_percent'] = convert_double_dash(
            values[20].text.strip(), float)
        new_row['sf_per_gp'] = convert_double_dash(
            values[21].text.strip(), float)
        new_row['sa_per_gp'] = convert_double_dash(
            values[22].text.strip(), float)
        new_row['fo_win_percent'] = float(values[23].text.strip())
        new_row['season'] = season
        new_row['page'] = page

        all_rows.append(new_row)
    
    return all_rows

def get_nhl_data(
        row_schema: dict, mongo_coll: collection, postgres_engine: Engine, 
        start_season: int, end_season: int=None) -> None:
    """Extract, parse, transform, and store data from NHL's official
    website.

    This function will extract HTML from the NHL's official website, 
    parse the HTML into a BeautifulSoup object, store the raw HTML into
    a MongoDB collection, extract the data stored in the HTML table into
    a list of dictionaries, transform the list of dictionaries into a
    Pandas dataframe, store the dataframe into a Postgres table, and repeat
    this process for all seasons and season pages from the given inputs.

    Parameters
    ----------
    row_schema : dict
        A dictionary that has HTML table row names as keys and `None` for
        values. This dictionary is a template for the table columns and
        cells to be extracted.

    mongo_coll : pymongo.collection.Collection
        A MongoDB collection to store the raw HTML data to.

    postgres_engine : sqlalchemy.engine
        Sqlalchemy engine to a PostgreSQL table to store the data from
        the HTML table.

    start_season : int
        Start season as a single integer. To start with data from the 
        2009-2010 season, input 2009.

    end_season : int, None
        End season as a single integer. To end with data from the 
        2009-2010 season, input 2009. If the argument is omitted, then
        the `start_season` is used for `end_season`.

    Returns
    -------
    None
        This function performs actions and does not return a value.
    """
    if end_season is None:
        end_season = start_season

    print('Starting web scraping...')
    for season in range(start_season, end_season+1):
        start_url = make_url(season)
        soup = get_soup(start_url)
        num_pages = int(soup.find('span', class_='-totalPages').text.strip())

        for page in range(num_pages):
            print(f'Starting season: {season}, page: {page} ...')

            if page > 0:
                new_url = make_url(season, page)
                soup = get_soup(new_url)
            
            mongo_coll.insert_one(
                {'season': season, 'page': page, 'soup': soup.prettify()})

            all_rows = extract_page_table(soup, season, page, row_schema)

            table = pd.DataFrame(all_rows)
            table.to_sql(
                'games', postgres_engine, index=False, if_exists='append')
            time.sleep(5)
    
    print(f'Web scraping complete.')
    return None


if __name__ == '__main__':
    start_season = 2019
    end_season = 2020

    mongo = MongoClient('localhost', 27017)
    db = mongo['nhl']
    coll = db['soup']

    engine = make_alchemy_engine('nhl')

    empty_row = {'team': None, 'game': None, 'gp': None, 'wins': None, 
                'losses': None, 'ties': None, 'ot_losses': None, 
                'points': None, 'point_percent': None, 'reg_wins': None, 
                'reg_ot_wins': None, 'so_wins': None, 'gf': None, 'ga': None, 
                'gf_per_gp': None, 'ga_per_gp': None, 'pp_percent': None, 
                'pk_percent': None, 'pp_net_percent': None, 
                'pk_net_percent': None, 'sf_per_gp': None, 'sa_per_gp': None, 
                'fo_win_percent': None, 'season': None, 'page': None}

    get_nhl_data(empty_row, coll, engine, start_season, end_season)

    mongo.close()
    engine.dispose()
