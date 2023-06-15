from pydantic import BaseModel, BaseSettings
from datetime import datetime
from typing import Optional

class HodlHodlOfferBase(BaseModel):
    def __init__(self, **offer):
        # data["coin_currency"] = "bitcoin"
        self.offer_identifier=offer.get("id"),
        self.fiat_currency=offer.get("asset_code"),
        self.country_code=offer.get("country_code"),
        self.trading_type_name=offer.get("side"),
        self.trading_type_slug=offer.get("side"),
        self.payment_method_name=offer.get("payment_methods")[0].get("type") if offer.get("payment_methods") else None,
        self.payment_method_slug=offer.get("payment_methods")[0].get("type") if offer.get("payment_methods") else None,
        self.description=offer.get("description"),
        self.currency_code=offer.get("currency_code"),
        self.coin_currency=offer.get("currency_code"),
        self.price=offer.get("price"),
        self.min_trade_size=offer.get("min_amount"),
        self.max_trade_size=offer.get("max_amount"),
        self.site_name='hodlhodl',
        self.margin_percentage=0,
        self.headline=''
        return super().__init__(**offer)

    trading_type_name: str
    trading_type_slug: str
    coin_currency: str
    fiat_currency: str
    payment_method_slug: str
    payment_method_name: str

    country_code: str
    min_trade_size: str
    max_trade_size: str

    margin_percentage: float

    offer_identifier: str
    site_name: str

    headline: str

class HodlHodlUserBase(BaseModel):
    @classmethod
    def convert_date(cls, date):
        last_online = datetime.fromtimestamp(date).strftime("%Y-%m-%d")
        
        return last_online

    def __init__(self, **offer):
        self.username=offer.get("trader").get("login") if offer.get("trader") else None,
        self.feedback_score=offer.get("trader").get("rating") if offer.get("trader") else 0,
        self.completed_trades=offer.get("trader").get("trades_count") if offer.get("trader") else 0,
        self.profile_image='',
        self.trade_volume=0
        super().__init__(**offer)
        return super().__init__(**offer)

    username: str
    feedback_type: str = 'SCORE'
    feedback_score: float
    trade_volume: Optional[str]
    completed_trades: int

    profile_image: Optional[str]


class Settings(BaseSettings):
    

    class Config:
        env_file = '.env'
        env_file_encoding = "utf-8"


settings = Settings()