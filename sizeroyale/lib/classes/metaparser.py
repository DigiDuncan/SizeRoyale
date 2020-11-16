from sizeroyale.lib.attrdict import AttrDict
from sizeroyale.lib.errors import ParseError

class MetaParser:
    def __init__(self, t):
        self.t = t

    def parse(self, s):
        try:
            _ = self.t.valid_data
        except AttributeError:
            raise ParseError(f"Type {self.t} does not define valid metadata.")

        returndict = {}
        itemsdict = {}

        items = s.split(",")
        for item in items:
            item = item.strip()
            kv = item.split(":", 1)
            try:
                itemsdict[kv[0]] = kv[1]
            except IndexError:
                raise ParseError(f"Metatag {kv[0]} has no value.")
        for k, v in itemsdict.items():
            if k in ["size", "give", "remove"]:
                kv2 = v.split(":", 1)
                try:
                    v = AttrDict({kv2[0]: kv2[1]})
                except IndexError:
                    raise ParseError(f"Metatag {kv2[0]} has no value.")

        for key in self.t.valid_data:
            if key in itemsdict:
                returndict[key] = itemsdict[key]
            else:
                returndict[key] = None

        return AttrDict(returndict)
