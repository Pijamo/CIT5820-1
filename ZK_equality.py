from zksk import Secret, DLRep
from zksk import utils

def ZK_equality(G,H):

    #Generate two El-Gamal ciphertexts (C1,C2) and (D1,D2)
    #G, H = utils.make_generators(num=2, seed=42)
    r_1 = Secret(utils.get_random_num(bits=128))
    r_2=  Secret(utils.get_random_num(bits=128))
    k=Secret(utils.get_random_num(bits=128))
    
   
    C_1= r_1.value*G
    C_2=r_1.value*H + k.value*G
    D_1= r_2.value*G
    D_2=r_2.value*H+k.value*G
    
    s = DLRep(C_1,r_1*G)  & DLRep(D_1,r_2*G) & DLRep(D_2,r_2*H+k*G)& DLRep(C_2,r_1*H+k*G)
    zkp = s.prove()
    

    #Generate a NIZK proving equality of the plaintexts
    s.verify(zkp)

    #Return two ciphertexts and the proof
    return (C_1,C2), (D1,D_2), zkp