import socket
from utils import *
# from ntru import NTRUKey, generate_key
import pickle

N = 5
p = 3
q = 2051


class server:

    def __init__(self, km):
        self.registered_clients = {}
        self.km = km
        self.n = 0
        self.deln = 100

    def add_client(self, id, K, n):
        self.registered_clients[id] = [K, n]


def main():

    # HN = server(567890)

    #  add random clients

    # HN.add_client(234562345, 3452345, 1005)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((host, port))

    server_socket.listen(5)
    print("Server listening on {}:{}".format(host, port))

    client_socket, addr = server_socket.accept()
    print("Connection from {}".format(addr))

    # send_list(client_socket, [N,p,q,[2,3]])
    # keys = generate_key()
    # server_h = keys._h

    # client_socket.sendall(pickle.dumps(server_h))
    # client_pk = pickle.loads(client_socket.recv(8192))
    # client_pk = receive_list(client_socket)
    # print("Client Public Key", client_pk)
    # print(keys.get_h)


# **************** Registration Phase ****************

    km = get_random()
    HN = server(km)
    KFS = get_random()
    KFS = hash_function([KFS])
    kn = get_random()
    U_id = 234562345
    an = U_id ^ hash_function([km, kn])
    bn = an ^ km ^ kn
    c = hash_function([km, U_id])
    HN.add_client(U_id, KFS, 0)
    client_socket.sendall(pickle.dumps([KFS, U_id, an, bn, c, 0]))
    print("Message sent from HN to UE [KFS, U_id, an, bn, c, cnt]: ", [KFS, U_id, an, bn, c, 0], "\n")


# **************** Phase 2 ****************


    # response = receive_list(client_socket)
    response = pickle.loads(client_socket.recv(5120000))
    # response = keys.decrypt(response)
    # response = deserialize(response)
    # print(type(response),"hii")
    # print(response)
    id = -1
    for id_, value in HN.registered_clients.items():
        c_ = hash_function([HN.km, id_])
        kn_ = response[0] ^ hash_function([c_, response[4]]) ^ HN.km ^ response[1] ^ hash_function([c_, response[4] ^ id_])
        if id_ == response[0] ^ hash_function([c_, response[4]]) ^ hash_function([HN.km, kn_]):
            id = id_
            break
    
    if id == -1:
        abort("hiii")
    n_ = -1
    flag = 0
    if Truncate(hash_function([c, response[0]])) == response[2]:
        print("Message recieved from UE[an*, bn*, A, B, R, hn] : ", response, "\n")
        # sync mode
        KFS_ = HN.registered_clients[id_][0]
        nid = HN.registered_clients[id][1]
        for itr in range(HN.deln):
            x = hash_function([KFS_])
            if response[5] == hash_function([x, id, c, an, bn, nid + itr]):
                n_ = nid + itr
                flag = 1
            x = KFS
            if response[5] == hash_function([x, id, c, an, bn, nid + itr]):
                n_ = nid + itr
                flag = 0
        if n_ == -1:
            abbort()  
    else:
        print("Message recieved from UE[an*, bn*, yn, zn, R, hn] : ", response, "\n")
        rn = response[2] ^ an ^ id
        n_ = response[3] ^ hash_function([HN.km, rn, response[2]])
        KFS_ = HN.registered_clients[id_][0]
        nid = HN.registered_clients[id][1]
        for itr in range(1000):
            x = hash_function([KFS_])
            if response[5] == hash_function([x, id, c, an, bn, nid + itr, response[3]]):
                n_ = nid + itr
                flag = 1
            x = KFS
            if response[5] == hash_function([x, id, c, an, bn, nid + itr, response[3]]):
                n_ = nid + itr
                flag = 0
        if n_ == -1:
            abbort()  

        # desync mode


    if flag == 1:
        KFS_ = hash_function([KFS_])
        HN.registered_clients[id_][0] = KFS_
    
    HN.registered_clients[id][1] = n_ + 1
    kn_ = get_random()
    fn_ = get_random()
    an_ = id ^ hash_function([HN.km, kn_])
    bn_ = an_ ^ HN.km ^ kn_
    eeta = hash_function([fn_, c]) ^ an_
    muu = hash_function([c, fn_]) ^ bn_
    alpha = c ^ fn_
    seskey = hash_function([KFS_, fn_, eeta, muu, HN.registered_clients[id][1]+ 1])
    beta = hash_function([seskey, an_, bn_, id, c])  
    reply = [alpha, beta, eeta, muu]
    # print(reply)
    # print(type(reply ))
    # reply = keys.encrypt(reply, client_pk)
    client_socket.sendall(pickle.dumps(reply))
    print("Message sent from HN to UE[alpha, beta, eeta, muu]: ", reply, "\n")





    # kn = response[1] ^ response[2] ^ HN.km
    # id = response[1] ^ hash_function([HN.km, kn])
    # c = hash_function([HN.km, id])

    # if id not in HN.registered_clients.keys():
    #     print("1")
    #     abort()
    # # print(id, HN.km, kn,"\n\n\n")
    # K = HN.registered_clients[id][0]
    # n_ = HN.registered_clients[id][1]

    # if response[0] == 1:    # desync mode

    #     # response[1] -> an
    #     # response[2] -> bn
    #     # response[3] -> yn
    #     # response[4] -> zn
    #     # response[5] -> hn

    #     rn = response[3] ^ response[1] ^ id
    #     n = response[4] ^ hash_function([K, rn, response[3]])
    #     flag = False

    #     while n:
    #         if (
    #             hash_function([K, id, c, response[1], response[2], n, response[4]])
    #             == response[5]
    #         ):
    #             n_ = n
    #             flag = True
    #             break
    #         n -= 1
    #     if not flag:
    #         abort()
        
    # elif response[0] == 0:   # sync mode

    #     # response[1] -> an
    #     # response[2] -> bn
    #     # response[3] -> hn
    #     flag = False
    #     for itr in range(HN.deln):
    #         # print("hash ",[K, id, c, response[1], response[2], n])
    #         if hash_function([K, id, c, response[1], response[2], HN.registered_clients[id][1] + itr]) == response[3]:
    #             HN.registered_clients[id][1] = HN.registered_clients[id][1] + itr
    #             flag = True
    #             break
    #     if not flag:
    #         abort()
    # else:
    #     abort()

    # n_ = n_ + 1
    # kn_ = get_random()
    # fn_ = get_random()
    # an_ = id ^ hash_function([HN.km, kn_])
    # bn_ = an_ ^ HN.km ^ kn_
    # eeta = hash_function([fn_, c]) ^ an_
    # muu = hash_function([c, fn_]) ^ bn_
    # alpha = c ^ fn_
    # seskey = hash_function([K, fn_, eeta, muu, n_ + 1])
    # beta = hash_function([seskey, an_, bn_, id, c])
    # # print("hash",[seskey, an_, bn_, id, c])
    # # print("hash", hash_function([seskey, an_, bn_, id, c]))


    # # send_list(client_socket, [alpha, beta, eeta, muu])
    # # print(alpha, beta ,eeta ,muu)
    # # reply = serialize([alpha, beta, eeta, muu])
    # reply = [alpha, beta, eeta, muu]
    # # print(reply)
    # # print(type(reply ))
    # # reply = keys.encrypt(reply, client_pk)
    # client_socket.sendall(pickle.dumps(reply))

    print("Authentication Succesful")

    while True:

        data = client_socket.recv(1024).decode("utf-8")
        print("Received from client:", data)

        if data.lower() == "exit":
            break

        response = input("Enter message to send to client: ")
        client_socket.send(response.encode("utf-8"))

    client_socket.close()


if __name__ == "__main__":
    main()