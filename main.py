import random
from prefect import flow
import requests
from requests import RequestException
import time
from typing import Union
from logging import Logger
from schemas import (HodlHodlOfferBase, HodlHodlUserBase,
                                      settings)
from enum import Enum
from prefect import Task
from prefect.server.schemas.states import StateType

class Scraper_Names(Enum):
    hodlhodl = "hodlhodl"


class HodlhodlComScraper:
    def __init__(self, logger: Logger = None, proxy: dict = None, prefect: bool = False, **kwargs):
        self.proxy = proxy
        self.logger = logger 
        self.prefect = prefect
        self.requester = requests
        self.total_offer_percent_to_scrape = kwargs.get("total_offer_percent_to_scrape", 100)
        self.base_url = 'https://hodlhodl.com/api/frontend'

    def get_currency_list(self):
        url = f"{self.base_url}/currencies"
        currency_list = []
        try:
            currencies = self.requester.get(url).json()
            for curr in currencies['currencies']:
                currency_list.append(curr.get("code"))
        except RequestException as e:
            self.logger.error("Error fetching currency list: %s", e)

        return currency_list

    def get_and_post_offers(self, curr, trading_type):
        url = f"{self.base_url}/offers?filters[currency_code]={curr}&pagination[offset]=0&filters[side]={trading_type}&facets[show_empty_rest]=true&facets[only]=false&pagination[limit]=100"
        try:
            resp = self.requester.get(url).json()
            for offer in resp.get("offers"):
                offer_info = HodlHodlOfferBase(offer)
                seller_info = HodlHodlUserBase(offer)
                self.post_data_to_api(seller_info, offer_info)
        except RequestException as e:
            self.logger.error("Error fetching offers: %s", e)
        

    def post_data_to_api(self, seller_info, offer_info):
        data = {
            "user": seller_info.dict(),
            "offer": offer_info.dict(),
        }

        cc = offer_info.dict()["country_code"]
        if cc == "Global":
            cc = 'GL'

        params = {
            "country_code": cc,
            "payment_method": offer_info.dict()["payment_method_name"],
            "payment_method_slug": offer_info.dict()["payment_method_slug"],
        }

        try:
            return self.post_request_to_api(endpoint="local_traders/create_offer", data=data, params=params,
                                       logger=self.logger).json()
        except RequestException as e:
            self.logger.error("Error posting data to API: %s", e)
    
    def post_request_to_api(self, endpoint, data, params, logger):
        try:
            url = f"{self.base_url}/{endpoint}"
            return self.requester.post(endpoint=url, data= data, params= params)
        except RequestException as e:
            logger.error("Error posting data to API: %s", e)


    def starter_cli(self):
        currencies_list = self.get_currency_list()
        curr = random.choice(currencies_list)
        self.get_and_post_offers(curr, 'sell')

    def starter(self):
        currencies_list = self.get_currency_list()
        for curr in currencies_list:
            for trading_type in ['buy', 'sell']:
                if self.prefect:
                    rate = Task(self.get_and_post_offers, name=f"get hodlhodl offers").submit(curr, trading_type,
                                                                                             return_state=True)
                    if rate.type != StateType.COMPLETED or not rate.result():
                        self.logger.error('Task failed')
                        continue
                    self.count_offers(rate.result(), Scraper_Names.hodlhodl.name)
                    self.logger.debug("Got %s rates", rate)

                    offer_counter = self.get_counter(Scraper_Names.hodlhodl.name)
                    return offer_counter

                else:
                    self.get_and_post_offers(curr, trading_type)
            time.sleep(1)  # rate limiting
    def count_offers(self, rate, scraper_name):
        pass

    def get_counter(self, scraper_name):
        pass

@flow
def get_hodlhodl_offers():
    ag = HodlhodlComScraper()
    ag.starter()


if __name__ == "__main__":
    get_hodlhodl_offers()

