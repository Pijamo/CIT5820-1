from zksk import Secret, DLRep
from zksk import utils


def ZK_equality(G, H):
    # Generate two El-Gamal ciphertexts (C1,C2) and (D1,D2)
    # G, H = utils.make_generators(num=2, seed=42)
    r_1 = Secret(utils.get_random_num(bits=128))
    r_2 = Secret(utils.get_random_num(bits=128))
    m = Secret(utils.get_random_num(bits=128))

    C1 = r_1.value * G
    C2 = r_1.value * H + m.value * G
    D1 = r_2.value * G
    D2 = r_2.value * H + m.value * G

    st = DLRep(C1, r_1 * G) & DLRep(C2, r_1 * H + m * G) & DLRep(D1, r_2 * G) & DLRep(D2, r_2 * H + m * G)
    zkp = st.prove()

    # Generate a NIZK proving equality of the plaintexts
    st.verify(zkp)

    # Return two ciphertexts and the proof
    return (C1, C2), (D1, D2), zkp