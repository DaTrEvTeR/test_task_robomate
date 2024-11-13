from asyncio import sleep


async def delete_incorrect_with_timeout(msg):
    to_delete = await msg.answer("Incorrect format")
    await msg.delete()
    await sleep(7)
    return await to_delete.delete()
