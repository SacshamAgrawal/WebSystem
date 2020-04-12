import asyncio,glob
async def handle_echo(reader, writer):
    
    # Accepting request from clients
    data = await reader.read(1024)
    data = data.decode('latin-1')
    print(data)    

    # Returning Data for file
    file = glob.glob('index.html')[0]
    with open(file,'rb') as f:
        response = f.read()
        writer.write(response)
        await writer.drain()

    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server( handle_echo, '127.0.0.1', 5000)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
            await server.serve_forever()    

try:
    asyncio.run(main()) 
except KeyboardInterrupt:
    print("\nKeyboardInterrupt ...\nShuttingDown Server...\n")