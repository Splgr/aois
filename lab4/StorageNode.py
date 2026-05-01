ALPHABET_MAP = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
class StorageNode:
    __slots__ = ('position', 'keyword', 'flag_collision', 'flag_used', 
                 'flag_terminal', 'flag_link', 'flag_deleted', 
                 'pointer_next', 'payload', 'val_v', 'base_h')
    def __init__(self, idx):
        self.position = idx
        self.keyword = ""
        self.flag_collision = 0    # C
        self.flag_used = 0         # U
        self.flag_terminal = 1     # T
        self.flag_link = 0         # L 
        self.flag_deleted = 0      # D
        self.pointer_next = idx    # P0
        self.payload = ""
        self.val_v = 0
        self.base_h = 0

def encode_key(phrase: str) -> int:
    clean = phrase.strip().lower()
    if not clean: return 0
    c1 = clean[0]
    c2 = clean[1] if len(clean) > 1 else "а"
    v1 = ALPHABET_MAP.find(c1) if c1 in ALPHABET_MAP else 0
    v2 = ALPHABET_MAP.find(c2) if c2 in ALPHABET_MAP else 0
    return v1 * 33 + v2