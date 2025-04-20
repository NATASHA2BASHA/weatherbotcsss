
from aiogram.fsm.state import StatesGroup, State

class MenuState(StatesGroup):
    forecast_menu = State()
    details_menu = State()

class ForecastState(StatesGroup):
    waiting_for_city = State()

class DetailsState(StatesGroup):
    waiting_for_city = State()

class SubscriptionState(StatesGroup):
    choosing_action = State()
    subscribing_city = State()
    unsubscribing_city = State()
