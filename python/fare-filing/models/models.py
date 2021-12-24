from pydantic import BaseModel
from typing import List, Optional


class WorkPackageRecord(BaseModel):
    """Class for keeping track of all information needed for work package"""
    # declare constants
    origin: str = 'NYC'
    destination: str
    fare_basis: str
    booking_class: str
    cabin: str
    ow_rt: str
    blank1: str
    blank2: str
    blank3: str
    currency: str = 'USD'
    fare_price: float
    season: str


class WorkPackage(BaseModel):
    data: List[WorkPackageRecord]


class CabinMapping(BaseModel):
    booking_class: dict
    cabin: dict
    rt_only: dict
    weekend_only: dict


class SeasonMapping(BaseModel):
    season: dict
    season_code: dict


class FareCombination(BaseModel):
    weekend: dict
    oneway_multiplier: dict
    weekend_surcharge: dict
    oneway: dict
    oneway_mapping: dict


class Input(BaseModel):
    dest: dict
    booking_class: dict
    season: dict
    base_fare: dict
    direct: dict
    cabin: dict
    rt_only: dict
    weekend_only: dict
    season_code: dict