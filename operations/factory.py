import datetime
from typing import Union, Any

from sqlalchemy import select, text

from database import async_session, RollOrm, sync_session
from operations.schemas import RollAdd, Roll, Dict_generator


class RollFactory:
    @classmethod
    async def add_one_roll(cls, data: RollAdd) -> int:
        async with async_session() as session:
            roll_dict = data.model_dump()

            print(1)
            roll = RollOrm(**roll_dict)
            try:
                print(2)
                session.add(roll)
                await session.flush()
                print(3)
            except Exception:
                print(4)
                return -1
            else:
                print(5)
                await session.flush()
                await session.commit()
                return roll.id

    @classmethod
    async def find_all(cls, sorting_properties: str) -> list[Roll]:
        async with async_session() as session:
            if sorting_properties != '':
                query = select(RollOrm).order_by(text(sorting_properties))
            else:
                query = select(RollOrm)
            result = await session.execute(query)
            roll_models = result.scalars().all()
            roll_schemas = [Roll.model_validate(roll_model) for roll_model in roll_models]
            return roll_schemas

    @classmethod
    def delete_roll_info(cls, roll_id: str) -> bool:
        with sync_session() as session:
            roll = session.get(RollOrm, int(roll_id))
            if roll is None:
                return False
            else:
                session.delete(roll)
                session.commit()
                return True

    @classmethod
    def delete_roll(cls, roll_id: str, removed_date: str) -> bool:
        with sync_session() as session:
            roll = session.get(RollOrm, int(roll_id))
            if roll is None:
                return False
            else:
                roll.removed_date = removed_date
                session.commit()
                return True

    @classmethod
    def get_roll_by_id(cls, roll_id: str) -> dict:
        with sync_session() as session:
            roll = session.query(RollOrm).get(roll_id)
            if roll is None:
                return {"status": False, "roll_id": roll_id, "length": 0, "weight": 0, "added_date": 0,
                        "removed_date": 0}
            else:
                return {"status": True, "roll_id": roll_id, "length": roll.length, "weight": roll.weight,
                        "added_date": roll.added_date, "removed_date": roll.removed_date}

    @classmethod
    async def count_added(cls, start_date: str, end_date: str) -> int:
        async with async_session() as session:
            query = select(RollOrm).filter(
                RollOrm.added_date.between(start_date, end_date),
                RollOrm.removed_date.is_(None)  # RollOrm.removed_date <= end_date
            )
            result = await session.execute(query)
            roll_models = result.scalars().all()
            roll_schemas = [Roll.model_validate(roll_model) for roll_model in roll_models]

        length = len(roll_schemas)
        return length

    @classmethod
    async def count_removed(cls, start_date: str, end_date: str) -> int:
        async with async_session() as session:
            query = select(RollOrm).filter(
                RollOrm.added_date.between(start_date, end_date),
                RollOrm.removed_date.isnot(None)
            )
            result = await session.execute(query)
            roll_models = result.scalars().all()
            roll_schemas = [Roll.model_validate(roll_model) for roll_model in roll_models]

        length = len(roll_schemas)
        return length

    @classmethod
    async def mean_length_weight(cls, start_date: str, end_date: str) -> tuple[Union[float, Any], Union[float, Any]]:
        async with async_session() as session:
            query = select(RollOrm).filter(
                RollOrm.added_date.between(start_date, end_date)
            )
            result = await session.execute(query)
            roll_models = result.scalars().all()
            total_length = sum([roll.length for roll in roll_models])
            total_weight = sum([roll.weight for roll in roll_models])

            average_length = total_length / len(roll_models)
            average_weight = total_weight / len(roll_models)

        return average_length, average_weight

    @classmethod
    async def min_max_length_weight(cls, start_date: str, end_date: str) -> tuple[
        Union[int, Any], Union[int, Any], Union[int, Any], Union[int, Any]]:
        async with async_session() as session:
            query = select(RollOrm).filter(
                RollOrm.added_date.between(start_date, end_date)
            )
            result = await session.execute(query)
            roll_models = result.scalars().all()

            max_length = max([roll.length for roll in roll_models]) if roll_models else 0
            min_length = min([roll.length for roll in roll_models]) if roll_models else 0

            max_weight = max([roll.weight for roll in roll_models]) if roll_models else 0
            min_weight = min([roll.weight for roll in roll_models]) if roll_models else 0

        return min_length, max_length, min_weight, max_weight

    @classmethod
    async def sum_length_weight(cls, start_date: str, end_date: str) -> tuple[Union[int, Any], Union[int, Any]]:
        async with async_session() as session:
            query = select(RollOrm).filter(
                RollOrm.added_date.between(start_date, end_date)
            )
            result = await session.execute(query)
            roll_models = result.scalars().all()
            total_length = sum([roll.length for roll in roll_models])
            total_weight = sum([roll.weight for roll in roll_models])

        return total_length, total_weight

    @classmethod
    async def min_max_datadiff(cls, start_date: str, end_date: str) -> tuple[int, int]:
        async with async_session() as session:
            query = select(RollOrm).filter(
                RollOrm.added_date.between(start_date, end_date),
                RollOrm.removed_date.isnot(None)
            )
            result = await session.execute(query)
            roll_models = result.scalars().all()

            durations = [(datetime.datetime.strptime(roll.removed_date, "%d.%m.%Y") -
                          datetime.datetime.strptime(roll.added_date, "%d.%m.%Y")).days for roll in roll_models]

            max_duration_days = max(durations, default=0) if durations else 0
            min_duration_days = min(durations, default=0) if durations else 0

        return min_duration_days, max_duration_days

    @classmethod
    async def min_max_inventory_days(cls, start_date: str, end_date: str) -> tuple[Any, Any]:
        date_format = '%d.%m.%Y'
        step = datetime.timedelta(days=1)
        start_date = datetime.datetime.strptime(start_date, date_format)
        end_date = datetime.datetime.strptime(end_date, date_format)
        dictionary = Dict_generator()
        while start_date <= end_date:
            dictionary.add_el(await cls.count_added(start_date.strftime(date_format), start_date.strftime(date_format)),
                              start_date.strftime(date_format))

            start_date += step

        dictionary = dictionary.dictionary
        dictionary = dict(sorted(dictionary.items(), key=lambda item: item[0]))

        min_date, max_date = list(dictionary.items())[0][1], list(dictionary.items())[-1][1]
        return min_date, max_date

    @classmethod
    async def min_max_wight_days(cls, start_date: str, end_date: str)-> tuple[str, str]:
        date_format = '%d.%m.%Y'
        step = datetime.timedelta(days=1)
        start_date = datetime.datetime.strptime(start_date, date_format)
        end_date = datetime.datetime.strptime(end_date, date_format)
        dictionary = Dict_generator()
        while start_date <= end_date:
            _, weight = await cls.sum_length_weight(start_date.strftime(date_format), start_date.strftime(date_format))
            dictionary.add_el(weight, start_date.strftime(date_format))

            start_date += step

        dictionary = dictionary.dictionary
        dictionary = dict(sorted(dictionary.items(), key=lambda item: item[0]))

        min_date, max_date = list(dictionary.items())[0][1], list(dictionary.items())[-1][1]
        return min_date, max_date
