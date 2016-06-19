__author__ = 'Vincent'
from sqlalchemy.ext.declarative import DeclarativeMeta
import json
import utils.log as log


def new_alchemy_encoder(revisit_self=False, fields_to_expand=[], nested_object=True):
    _visited_objs = []

    class AlchemyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                # don't re-visit self
                if revisit_self:
                    if obj in _visited_objs:
                        return None
                    _visited_objs.append(obj)

                # go through each field in this SQLalchemy class
                fields = {}
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                    sql_alchemy_object = False
                    val = obj.__getattribute__(field)

                    # is this field another SQLalchemy object, or a list of SQLalchemy objects?
                    if isinstance(val.__class__, DeclarativeMeta) or (
                            isinstance(val, list) and len(val) > 0 and isinstance(val[0].__class__, DeclarativeMeta)):
                        sql_alchemy_object = True
                        # unless we're expanding this field, stop here
                        if field not in fields_to_expand:
                            # not expanding this field: set it to None and continue
                            # fields[field] = None
                            continue

                    # fields[field] = val
                    log.log("Field: %s | val %s isoformat: %s" % (field, val, val.isoformat() if hasattr(val, 'isoformat') else ""), log.LEVEL_DEBUG)
                    if not sql_alchemy_object or (sql_alchemy_object and nested_object):
                        log.log("DEDANNNNNNNNNNNNNNNNNS", log.LEVEL_DEBUG)
                        fields[field] = val.isoformat() if hasattr(val, 'isoformat') else val
                # a json-encodable dict
                return fields

            return json.JSONEncoder.default(self, obj)

    return AlchemyEncoder