from core.exceptions import InvalidBitArrayError

class BitArray:
    def __init__(self, bits=None, size=32):
        self.size = size
        if bits is None:
            self.bits = [0] * size
        else:
            if len(bits) != size:
                raise InvalidBitArrayError(f"Ожидалось {size} бит, получено {len(bits)}")
            if not all(b in (0, 1) for b in bits):
                raise InvalidBitArrayError("Массив должен содержать только 0 и 1")
            self.bits = bits.copy()
    
    def __getitem__(self, index):
        return self.bits[index]
    
    def __setitem__(self, index, value):
        if value not in (0, 1):
            raise InvalidBitArrayError("Бит должен быть 0 или 1")
        self.bits[index] = value
    
    def __len__(self):
        return len(self.bits)
    
    def __str__(self):
        return ''.join(map(str, self.bits))
    
    def copy(self):
        return BitArray(self.bits, self.size)
    
    def invert(self, start=0, end=None):
        if end is None:
            end = self.size
        for i in range(start, end):
            self.bits[i] = 1 - self.bits[i]
    
    def add_one(self, start=0):
        carry = 1
        for i in range(start, self.size):
            idx = self.size - 1 - (i - start)
            if idx < 0:
                break
            s = self.bits[idx] + carry
            self.bits[idx] = s % 2
            carry = s // 2
            if carry == 0:
                break