"""
Schema, type enforcement, making sure ducks are ducks, geese are like ducks, and things that ain't, ain't.

Created by Brantley Harris and Luke Opperman.
"""

class _nil(object): 
    """  An indicator that a value is not present. """
    def __str__(self):
        raise TypeError('nil cannot be str')
    def __nonzero__(self):
        raise TypeError('nil cannot be bool')
    def __call__(self, v):
        return self

nil = _nil()

class Any(object):
    """
        Describes a compound type that will attempt to use each type given durring
        initialization.  If any type works, it is immediately returned.  Any works, logically,
        like an OR function.
        
        >>> number = Any(int, float)
        >>> print number("2")
        2
        >>> print number("2.4")
        2.4
        
        >>> if_int = Any(int, nil)
        >>> if_int('1')
        1
        >>> if_int('a') == nil
        True
        
    """
    def __init__(self, *funcs):
        self.funcs = [Schema(f) for f in funcs]
        
    def __call__(self, value):
        for func in self.funcs:
            try:
                return func(value)
            except Exception, e:
                pass
        raise TypeError("Unable to convert %r with any: %r: %s" % (value, self.funcs, e))
    
    def __repr__(self):
        return "<Type: Any(%r)>" % (self.funcs,)

Or = Any

class All(Any):
    """
        Describes a compound type that will attempt to use all the types given in 
        initialization.  The result of each conversion is then handed to the next.  
        All works, logically, like an AND function.
        
        >>> digits = All(str, int)
        >>> print digits(15)
        15
        >>> print digits('apples') #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        TypeError: Unable to convert 'apples' with <type 'int'>...
        
    """
        
    def __call__(self, value):
        for func in self.funcs:
            try:
                value = func(value)
            except Exception, e:
                raise TypeError("Unable to convert %r with %r: %s" % (value, func, e))
        return value
        
And = All
Chain = All

class Constant(object):
    def __init__(self, value):
        self.value = value
    
    def __call__(self, x):
        return self.value
    
    def __repr__(self):
        return "<Constant %s>" % self.default

def Default(type_, d):
    '''
    >>> int_or_none = Default(int, None)
    >>> print int_or_none('a')
    None
    
    '''
    class default(Constant):
        
        def __repr__(self):
            return "<Default %s>" % self.value

    return Any(type_, default(d))

class SchemaError(ValueError):
    pass

class _Schema(object):
    def __init__(self):
        self.registry = {}
    
    def __call__(self, structure):
        for cls, schema_cls in self.registry.iteritems():
            if isinstance(structure, cls):
                return schema_cls(structure)
        if callable(structure):
            return structure
        raise SchemaError("A Schema object must either be a type with a registered Schema type, or a callable")

    def register(self, cls, schema_cls):
        self.registry[cls] = schema_cls

Schema = _Schema()
schema = Schema
        
class DictSchema(dict):
    """
        Models a dictionary schema.
        
        >>> person = Schema({
        ...          'name': str, 
        ...          'id': int,
        ...          'numbers': [str],
        ...      })
        >>> bob = {
        ...          'name': 'bob',
        ...          'id': '45',
        ...          'numbers': [4, 4]
        ...      }
        >>> print person(bob)['id']
        45
        >>> print person(bob)['numbers']
        ['4', '4']
        
        >>> person = Schema({
        ...          'name': Default(str, 'Person'), 
        ...          'id': int,
        ...          'numbers': [str],
        ...      })
        >>> bob = {
        ...          'id': '45',
        ...          'numbers': [4, 4]
        ...      }
        >>> print person(bob)['name']
        Person
        
        >>> person = Schema({
        ...          ('years on earth', 'age') : int
        ... })
        >>> print person({'years on earth': 4.2})['age']
        4
    """
    def __init__(self, values, all_optional=True, all_none=False):
        super(DictSchema, self).__init__(values)
        for k, v in self.items():
            if all_optional:
                self[k] = Any(v, nil)
            elif all_none:
                self[k] = Any(v, or_none)
            else:
                self[k] = Schema(v)
    
    def __call__(self, value):
        build = {}
        for k, type_ in self.items():
            field = k
            if isinstance(k, tuple):
                k, field = k
            v = type_(value.get(k, nil))
            if v is not nil:
                build[field] = v
        return build

Schema.register(dict, DictSchema)

class IterSchema(object):
    """
        Models a generator/iterator schema.
        
        >>> integers = IterSchema(int)
        >>> print integers((1,2,3)).next()
        1
        >>> print list(integers( [1,2,3] ))
        [1, 2, 3]
        
        >>> integers2 = Schema(iter([int]))
        >>> print integers2([1,2,3]).next()
        1
    """
    def __init__(self, type_):
        self.type = type_
    
    def __call__(self, value):
        for i in iter(value):
            v = self.type(i)
            if v is not nil:
                yield v

Schema.register(type(iter([])), lambda x: IterSchema(x.next()))
Schema.register(type(iter(())), lambda x: IterSchema(x.next()))

class ListSchema(IterSchema):
    """
        Models a list schema.  The list given can only be one type
        which will indicate a list of many or none of that type.
        
        >>> integers = Schema( [int] )
        >>> print integers( [1, '2', u'3'] )
        [1, 2, 3]
        
        >>> integers = Schema( [Any(int, nil)] )
        >>> print integers( [1, '2', 'apples'] )
        [1, 2]
    """
    def __init__(self, structure):
        self.type = Schema(structure[0])
            
    def __call__(self, value):
        return list(super(ListSchema, self).__call__(value))

Schema.register(list, ListSchema)

class SetSchema(IterSchema):
    """
        Models a set schema. 
        
        >>> integer_set = SetSchema(int)
        >>> integer_set([1,2,2,3])
        set([1, 2, 3])
        
        >>> integer_set2 = Schema(set([int]))
        >>> print integer_set2([1,2,2,3])
        set([1, 2, 3])
    """
    def __call__(self, value):
        return set(super(SetSchema, self).__call__(value))

Schema.register(set, lambda x: SetSchema(x.pop()))

class TupleSchema(object):
    """
        Models a tuple schema.  A tuple schema can be of any length
        the schema must match up, positionally to the value given
        to convert.
        
        >>> signature = Schema( (str, int, float) )
        >>> print signature([1.5] * 3)
        ('1.5', 1, 1.5)
        
        >>> signature = Schema( (str, int, nil) )
        >>> print signature([1.5] * 3)
        ('1.5', 1)
        
        >>> print signature([2])
        Traceback (most recent call last):
        ...
        SchemaError: Cannot complete schema, value doesn't have 3 elements
        >>> print signature([1,2,3,4])
        Traceback (most recent call last):
        ...
        SchemaError: Cannot complete schema, value doesn't have 3 elements
        
    """
    def __init__(self, structure):
        self.structure = tuple(Schema(x) for x in structure)
            
    def __call__(self, value):
        iter_structure = iter(self.structure)
        iter_value = iter(value)
        values = (type_(v) for type_, v in zip(iter_structure, iter_value))
        
        if self._any_leftover(iter_value, iter_structure):
            raise SchemaError("Cannot complete schema, value doesn't have %d elements" % len(self.structure))
        
        return tuple(x for x in values if x is not nil)

    def _any_leftover(self, *its):
        for it in its:
            try:
                it.next()
            except StopIteration:
                pass
            else:
                return True
        return False

Schema.register(tuple, TupleSchema)
