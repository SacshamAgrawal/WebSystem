import socket,glob,json
from pprint import pprint

# host and port
host = '127.0.0.1'
port =  53

def loadzones():
    zonefiles = glob.glob('*.zone')
    jsonzones = {}
    for zone in zonefiles:
        with open(zone) as zonedata:
            data = json.load(zonedata)
            zonename = data['$origin']
            jsonzones[zonename] = data    
    return jsonzones

zones = loadzones()

def getFlags(data):
    byte1 = data[:1]
    byte2 = data[1:2]
    
    # for 1st Byte
    QR = '1'
    OPCODE = ''
    for bit in range(1,5):
        OPCODE += str(ord(byte1)&(1<<bit));
    AA = '1'
    TC = '0'
    RD = '0'
    
    # for 2nd Byte
    RA = '0'
    Z = '000'
    RCODE = '0000'

    return int(QR+OPCODE+AA+TC+RD,2).to_bytes(1,byteorder='big')+int(RA+Z+RCODE).to_bytes(1,byteorder='big')

def getquestiondomain(data):
    findLen = 1
    expectedLength = 0
    questiondomain = ''
    domainparts = []
    x = 0;y = 0;
    for byte in data:
        if not byte:
            domainparts.append(questiondomain)
            break
        elif not findLen:
            questiondomain += chr(byte)
            x += 1;
            if x == expectedLength:
                expectedLength = 0
                domainparts.append(questiondomain)
                questiondomain = ''
                findLen = 1
        else:
            findLen = 0
            expectedLength = byte
            x = 0
        y += 1

    questiontype = data[y+1:y+3]
    return (domainparts,questiontype)

def getzone(domain):
    global zones
    zone_name = '.'.join(domain)
    return zones[zone_name]

def getrecs(data):
    domain, questiontype = getquestiondomain(data)
    qt = ''
    if questiontype == b'\x00\x01':
        qt = 'a'
    zone = getzone(domain)  
    return (zone, domain, qt)

def buildquestion(domain, qt):
    qbytes = b''
    for part in domain:
        qbytes += (len(part)).to_bytes(1,byteorder = 'big')
        for char in part:
            qbytes += ord(char).to_bytes(1,byteorder='big')
    
    if qt == 'a':
        qbytes += (1).to_bytes(2,byteorder='big')
    qbytes += (1).to_bytes(2,byteorder='big')
    return qbytes

def rectobytes(domain,recqt,record,default_ttl):
    
    rbytes = b'\xc0\x0c'
    if(recqt == 'a'):
        rbytes += b'\x00\x01'
    rbytes += bytes([0])+bytes([1])
    if 'ttl' not in record:
        recttl = default_ttl
    else:
        recttl = record['ttl']
    rbytes += int(recttl).to_bytes(4,byteorder='big')
    if recqt == 'a':
        rbytes += bytes([0]) + bytes([4])
    for part in record['ip'].split('.'):
        rbytes += bytes([int(part)])
    return rbytes       

def buildResponse(data):
    
    # TransactionID
    TID = data[:2]

    # Flags
    flags = getFlags(data[2:4])

    # Question Count
    QDCOUNT = b'\x00\x01' 

    records, domain, questiontype  = getrecs(data[12:])
    # Answere Count
    ANCOUNT = (len(records[questiontype])).to_bytes(2,byteorder='big')

    # NameServer Count
    NSCOUNT = (0).to_bytes(2,byteorder='big')

    # Additional Records
    ARCOUNT = (0).to_bytes(2,byteorder='big')

    dnsheader = TID + flags + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT

    # DNS Question
    dnsquestion = buildquestion(domain,questiontype)

    # DNS Body
    dnsbody = b''
    for record in records[questiontype]:
        dnsbody += rectobytes(domain,questiontype,record,records["$ttl"])
    
    return dnsheader+dnsquestion+dnsbody

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind((host,port))
    print("Starting DNS Server at {}:{}".format(host,port))
    try:
        while True:
            data ,addr = sock.recvfrom(1024)
            r = buildResponse(data)
            pprint(r)
            sock.sendto(r,addr)
    except KeyboardInterrupt:
        print("\nShutting Down the DNS Server....\n")