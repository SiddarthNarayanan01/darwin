import asyncio

async def looper():
    i = 0
    while True:
        print(f'Printing {i}')
        i += 1
        await asyncio.sleep(0.5)

async def main():
    print('Starting')
    future = asyncio.ensure_future(looper())

    print('Waiting for a few seconds')
    await asyncio.sleep(4)

    print('Cancelling')
    future.cancel()

    print('Waiting again for a few seconds')
    await asyncio.sleep(2)

    print('Done')

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
