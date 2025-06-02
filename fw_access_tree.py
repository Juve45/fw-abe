import pyrelic

class Node:

    def __init__(self):
        self.children = []
        self.weights = []
        self.threshold = 0

    def add_child(self, node : 'Node', weight : int):
        self.children.append(node)
        self.weights.append(weight)


def modexp(base, exponent, modulus):
    result = 1
    base = base % modulus
    while exponent > 0:
        if exponent & 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent >>= 1
    return result


def eval(a, x, mod) -> int:
    ans = pyrelic.neutral_BN()

    for i in range(len(a)):
        ans += a[i] * modexp(x, i, mod)
        ans %= pyrelic.BN_from_int(mod)
    return ans


def mod_inv(a, p):
    return modexp(a, p - 2, p)  # Fermat's little theorem



def lagrange_coefficient(xi, x_values, x, mod):
    
    numerator = 1
    denominator = 1
    for j, xj in enumerate(x_values):
        if xj != xi:
            numerator = (numerator * (x - xj)) % mod
            denominator = (denominator * (xi - xj)) % mod
    return (numerator * mod_inv(denominator, mod)) % mod



class FWAccessTree:

    def __init__(self, root, public_key):
        self.root = root
        self.pk = public_key

    def share(self, values: list[int], results: dict, root: Node = None):

        if root is None:
            root = self.root

        if len(root.children) == 0:
            results[root.attribute] = values
            return

        parts = [[] for i in range(len(root.children))]
        wsum = sum(root.weights)

        for value in values:
            a = [value] + [pyrelic.rand_BN_mod(pyrelic.BN_from_int(self.pk.mod)) for i in range(root.threshold - 1)]

            k = 1
            for i in range(len(root.children)):
                for j in range(root.weights[i]):
                    parts[i].append(eval(a, k, self.pk.mod));
                    k += 1

        for i in range(len(root.children)):
            self.share(parts[i], results, root.children[i])


    def _collect_parts(self, D: dict, ct, root: Node):
        parts = []
        x_values = []
        offset = 1
        num_values = None

        for i, child in enumerate(root.children):
            child_parts = self.recon(D, ct, child)
            parts.append(child_parts)

            if child_parts is not None:
                assert len(child_parts) % root.weights[i] == 0
                num_values = len(child_parts) // root.weights[i]
                x_values.extend(range(offset, offset + root.weights[i]))

            offset += root.weights[i]

        return parts, x_values[:root.threshold], num_values


    def _combine_parts(self, parts, x_values, root: Node, num_values):
        if len(x_values) < root.threshold or num_values is None:
            return None

        ans = []
        for i in range(num_values):
            prod = pyrelic.neutral_GT()
            req = root.threshold
            tot = 0

            for j, child_parts in enumerate(parts):
                if child_parts is None:
                    tot += root.weights[j]
                    continue

                curr_parts = child_parts[i*root.weights[j]: (i+1)*root.weights[j]]
                start = tot + 1
                tot += root.weights[j]

                for k in range(root.weights[j]):
                    prod *= curr_parts[k] ** lagrange_coefficient(start + k, x_values, 0, self.pk.mod)
                    req -= 1
                    if req == 0:
                        break

                if req == 0:
                    break

            ans.append(prod)
        return ans


    def recon(self, D: dict, ct, root: Node = None):

        if root == None:
            root = self.root

        if len(root.children) == 0:
            attr = root.attribute
            if ct.Ts[attr] == None or D[attr] == None:
                return None
            

            return [pyrelic.pair(D[attr][i], ct.Ts[attr]) for i in range(len(D[attr]))]


        parts, x_values, num_values = self._collect_parts(D, ct, root)
        
        ret = self._combine_parts(parts, x_values, root, num_values)
        return ret
        