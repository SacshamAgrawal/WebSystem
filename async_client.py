import asyncio, urllib.parse, dns.resolver
from pprint import pprint

HOST = '127.0.0.1'
SERVER_PORT = 5000                     # port of server hosting
DNS_PORT = 53                          # port of dns server hosting

async def tcp_client():
    # Take url input
    print("Enter the url:")
    url = 'http://'+input('http://')
    url = urllib.parse.urlsplit(url)
    
    # Resolve the hostname using DNS Server
    host_ip = ''
    myresolver = dns.resolver.Resolver()
    myresolver.nameservers = ['127.0.0.1']
    try:
        response = myresolver.query(url.hostname)
        for ip in response:
            host_ip = str(ip)
    except:
        print("Cannot resolve the hostname...")
        return 

    # Make connection using url to the server
    reader, writer = await asyncio.open_connection(host_ip,SERVER_PORT)
    
    # Making GET request query 
    query = (f'GET {url.path or "/"} HTTP/1.0\n'
             f'Host: {url.hostname}\n')

    # Sending Request to Server
    print(f"Resolving to {writer.get_extra_info('peername')}")
    writer.write(query.encode('latin-1'))
    
    # Printing the response
    response = await reader.read()
    response = response.decode()
    print(response)

    # Closing the Connection
    writer.close()
    await writer.wait_closed()

asyncio.run(tcp_client())