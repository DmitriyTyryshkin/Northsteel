import re
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from database import delete_tables, create_tables
from operations.factory import RollFactory
from operations.schemas import RollAdd, Roll

router = APIRouter(
    prefix="/rolls",
    tags=["Стальные рулоны"],
)


def check_string(s):
    pattern = re.compile(r'\d{2}.\d{2}.\d{4}')
    if pattern.match(s):
        return True
    else:
        return False


@router.post("/add_roll")
async def add_roll(
        roll: Annotated[RollAdd, Depends()],
) -> JSONResponse:
    if check_string(roll.added_date) and check_string(roll.removed_date):
        roll_id = await RollFactory.add_one_roll(roll)
        return JSONResponse(status_code=200, content={f"рулон {roll_id} успешно добавлен"})
    else:
        return JSONResponse(status_code=400, content={"message": f"added_date или removed_date "
                                                                 f"не соотвествует формату даты (дд.мм.гггг)"})


@router.get("/get_rolls")
async def get_rolls(sorting_properties: str = '') -> list[Roll]:
    rolls = await RollFactory.find_all(sorting_properties)
    return rolls


@router.get("/get_statistic")
async def get_statistic(parameter: str, start_date: str, end_date: str) -> JSONResponse:
    if check_string(start_date) and check_string(end_date):
        if parameter == "count_added":
            count = await RollFactory.count_added(start_date, end_date)
            return JSONResponse(status_code=200, content={"message": f"рулонов добавлено: {count}."})

        elif parameter == "count_removed":
            count = await RollFactory.count_removed(start_date, end_date)
            return JSONResponse(status_code=200, content={"message": f"рулонов удалено: {count}."})

        elif parameter == "mean_length_weight":
            length, weight = await RollFactory.mean_length_weight(start_date, end_date)
            return JSONResponse(status_code=200, content={"message": f"средняя длина: {length}; "
                                                                     f" средний вес: {weight}."})

        elif parameter == "min_max_length_weight":
            min_length, max_length, min_weight, max_weight = await RollFactory.min_max_length_weight(start_date,
                                                                                                     end_date)
            return JSONResponse(status_code=200, content={"message": f"длина: {min_length} - {max_length}; "
                                                                     f"вес: {min_weight} - {max_weight}."})

        elif parameter == "sum_length_weight":
            length, weight = await RollFactory.sum_length_weight(start_date, end_date)
            return JSONResponse(status_code=200, content={"message": f"суммарная длина: {length}; "
                                                                     f"суммарный вес: {weight}."})

        elif parameter == "min_max_datadiff":
            min_duration_days, max_duration_days = await RollFactory.min_max_datadiff(start_date, end_date)
            return JSONResponse(status_code=200, content={
                "message": f"минимальный промежуток хранения: {min_duration_days}; "
                           f"максимальный промежуток хранения: {max_duration_days}."})

        elif parameter == "min_max_inventory_days":
            min_date, max_date = await RollFactory.min_max_inventory_days(start_date, end_date)
            return JSONResponse(status_code=200,
                                content={"message": f"День минимальной загрузки склада по количеству: {min_date}; "
                                                    f"день максимальной загрузки склада по количеству: {max_date}."})

        elif parameter == "min_max_wight_days":
            min_date, max_date = await RollFactory.min_max_wight_days(start_date, end_date)
            return JSONResponse(status_code=200,
                                content={"message": f"День минимальной загрузки склада по весу: {min_date}; "
                                                    f"день максимальной загрузки склада по весу: {max_date}."})

        else:
            return JSONResponse(status_code=404, content={"message": f"Команда {parameter} не существует"})

    else:
        JSONResponse(status_code=400, content={"message": f"start_date или end_date не соотвествует формату даты "
                                                          f"(дд.мм.гггг)"})


@router.get("/get_all_statistic")
async def get_statistic(start_date: str, end_date: str) -> JSONResponse:
    if check_string(start_date) and check_string(end_date):
        count_added = await RollFactory.count_added(start_date, end_date)
        count_removed = await RollFactory.count_removed(start_date, end_date)
        mean_length, mean_weight = await RollFactory.mean_length_weight(start_date, end_date)
        min_length, max_length, min_weight, max_weight = await RollFactory.min_max_length_weight(start_date, end_date)
        sum_length, sum_weight = await RollFactory.sum_length_weight(start_date, end_date)
        min_duration_days, max_duration_days = await RollFactory.min_max_datadiff(start_date, end_date)
        min_inventory_day, max_inventory_day = await RollFactory.min_max_inventory_days(start_date, end_date)
        min_wight_day, max_wight_day = await RollFactory.min_max_wight_days(start_date, end_date)

        return JSONResponse(status_code=200, content={"message":
                                                          f"рулонов добавлено: {count_added}; "
                                                          f"рулонов удалено: {count_removed}; "
                                                          f"средняя длина: {mean_length}; "
                                                          f"средний вес: {mean_weight}; "
                                                          f"длина: {min_length} - {max_length}; "
                                                          f"вес: {min_weight} - {max_weight}; "
                                                          f"суммарная длина: {sum_length}; "
                                                          f"суммарный вес: {sum_weight}; "
                                                          f"минимальный промежуток хранения: {min_duration_days}; "
                                                          f"максимальный промежуток хранения: {max_duration_days}; "
                                                          f"День минимальной загрузки склада по количеству: {min_inventory_day}; "
                                                          f"день максимальной загрузки склада по количеству: {max_inventory_day}; "
                                                          f"День минимальной загрузки склада по весу: {min_wight_day}; "
                                                          f"день максимальной загрузки склада по весу: {max_wight_day}."
                                                      })
    else:
        JSONResponse(status_code=400, content={"message": f"start_date или end_date не соотвествует формату даты "
                                                          f"(дд.мм.гггг)"})


@router.get("/get_one_roll")
def get_one_roll(roll_id: str) -> JSONResponse:
    response = RollFactory.get_roll_by_id(roll_id)
    if response["status"]:
        return JSONResponse(status_code=200, content={f"Информация о рулоне {roll_id}: длина- {response['status']}, "
                                                      f"вес- {response['status']}, "
                                                      f"дата добавления- {response['status']}, "
                                                      f"дата удаления- {response['status']}"})
    else:
        return JSONResponse(status_code=404, content={"message": f"Рулон {roll_id} не найден"})


@router.delete("/remove_roll")
def remove_roll(roll_id: str, removed_date: str) -> JSONResponse:
    if check_string(removed_date):
        response = RollFactory.delete_roll(roll_id, removed_date)
        if response:
            return JSONResponse(status_code=200,
                                content={"message": f"Запись об удалении рулона {roll_id} добавлена"})
        else:
            return JSONResponse(status_code=404, content={"message": f"Рулон {roll_id} не найден"})
    else:
        JSONResponse(status_code=400, content={"message": f"removed_date не соотвествует формату даты "
                                                          f"(дд.мм.гггг)"})


@router.delete("/remove_roll_info")
def remove_roll_info(roll_id: str) -> JSONResponse:
    response = RollFactory.delete_roll_info(roll_id)
    if response:
        return JSONResponse(status_code=200, content={"message": f"Ифнормация о рулоне {roll_id} удалена"})
    else:
        return JSONResponse(status_code=404, content={"message": f"Рулон {roll_id} не найден"})


@router.delete("/clear_db")
async def clear_db():
    await delete_tables()
    await create_tables()
    return JSONResponse(status_code=200, content={"message": f"База очищена"})
