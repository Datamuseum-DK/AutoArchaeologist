
import autoarchaeologist
import autoarchaeologist.scattergather as scattergather

class R1K_Tape_blocks():

    def __init__(self, this):
        if not this.has_type("TAPE file"):
            return
        print("?R1KT", this)
        l = []
        b = []
        for n, r in enumerate(this.iterrecords()):
            if not 0x30 <= r[0] <= 0x33:
                return
            p = 0
            while p < len(r):
                head = r[p:p+5].tobytes().decode('ASCII')
                i = int(head, 10)
                j = i // 10000
                assert 0 <= j <= 3
                k = i % 10000
                #print("  %05d %d %04d %s" % (p, j, k, str(r[p + 5:p + 5 + min(k - 5, 40)].tobytes())))
                if j < 2:
                    l.append([r[p+5:p+k]])
                else:
                    l[-1].append(r[p+5:p+k])
                p += k
        #print("L", l)
        ll = []
        for i in l:
            if len(i) == 1:
                ll += i
            else:
                #print("SG", i)
                ll.append(scattergather.ScatterGather(i))
        #print("LL", ll)
        y = this.create(start=0, stop=len(this), records=ll)
        this.add_type("R1K_PHYSICAL_TAPE")
        y.add_type("R1K_LOGICAL_TAPE")
