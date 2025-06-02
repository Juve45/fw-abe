import pyrelic


import aes

def hash(gt):
	s = ''
	j = 1
	for i in gt.coeffs:
		s += str(i) + str(j)
	return int(s) % 2**128





class PublicKey:
	pass

class MasterKey:
	pass

class Ciphertext:
	pass

class DecryptionKey:

	def __init__(self):
		self.access_structure = None

class FWABE:


	def __init__(self, maxAttributes = 10):
		self.pk = PublicKey()
		self.msk = MasterKey()

		self.pk.g1 = pyrelic.generator_G1()
		self.pk.g2 = pyrelic.generator_G2()
		self.pk.gT = pyrelic.pair(self.pk.g1, self.pk.g2)

		self.pk.n = maxAttributes 
		self.pk.mod = int(pyrelic.order())

		self.msk.t = [ pyrelic.rand_BN_order() for i in range(self.pk.n)]
		self.pk.T = [ self.pk.g2 ** t for t in self.msk.t]
		self.msk.y = pyrelic.rand_BN_order()
		self.pk.Y = self.pk.gT ** self.msk.y


	def encrypt(message, attributes, pk):
		ct = Ciphertext()
		# s = pyrelic.BN_from_int(1)
		s = pyrelic.rand_BN_order()
		ct.E = message * pk.Y ** s
		ct.Ts = [ti ** s if i in attributes else None for i, ti in enumerate(pk.T)]
		return ct

	def keygen(self, access_structure):
		results = {}
		dk = DecryptionKey()
		access_structure.share([self.msk.y], results)
		dk.access_structure = access_structure

		dk.D = dict()
		for i in range(self.pk.n):
			dk.D[i] = []
			if i not in results:
				dk.D[i] = None 
				continue
			for j in results[i]:
				exponent = j * self.msk.t[i].mod_inv(pyrelic.order())
				dk.D[i].append(self.pk.g1 ** exponent)
		
		return dk




	def decrypt(self):
		pass



fwabe = FWABE()

# x = add(fwabe.gT, fwabe.gT)
# print(x)
# print(hash(fwabe.pk.gT))


import time

xx = fwabe.pk.gT ** 745

start = time.perf_counter()
# code to benchmark
ct = FWABE.encrypt(xx, [0, 2, 3, 4, 5], fwabe.pk)
end = time.perf_counter()

print("Duration:", (end - start)*1000, "milliseconds")

from fw_access_tree import Node, FWAccessTree

a = [Node() for i in range(7)]
for i in range(7):
	a[i].attribute = i

g1 = Node()
g1.threshold = 5
g1.add_child(a[0], 2)
g1.add_child(a[1], 3)
g1.add_child(a[2], 5)
g2 = Node()
g2.threshold = 4
g2.add_child(a[3], 1)
g2.add_child(a[4], 2)
g2.add_child(a[5], 2)
g2.add_child(a[6], 3)
root = Node()

root.add_child(g1, 2)
root.add_child(g2, 2)
root.threshold = 4

acs = FWAccessTree(root, fwabe.pk)

dk = fwabe.keygen(acs);
# acs.share([pyrelic.BN_from_int(745)], )


ret = acs.recon(dk.D, ct)
print(ct.E / ret[0])
print(xx)



# for i in range(len(a)):
# 	a[i].shares = [multiply(G2, x * mod_inv(fwabe.t[i], fwabe.mod)) for x in a[i].shares]

# for i in range(len(a)):
# 	print(a[i].attribute, len(a[i].shares))

# a[0].shares = None
# a[1].shares = None
# a[3].shares = None
# a[4].shares = None

# for i in range(len(a)):
# 	if a[i].shares is not None:
# 		print(a[i].attribute, len(a[i].shares))

# print("started recon")

# res = recon(root, fwabe.mod, fwabe)
# print(res)

