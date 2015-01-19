# Bitmap

A Simple Python Implementation of Bitmap


## Normal Bitmap

```Python
>>> from bit_map import Bitmap
>>> bm = Bitmap( 20000000 ) # 20000000 is optional
>>> bm.turnOn( 123456 )
>>> bm.isTurnOn( 123456 )
True

>>> bm.turnOff( 123456 )
>>> bm.isTurnOn( 123456 )
False

>>> bm.turnOn( 300000000000 )   # *NOTICE*: with caution, this may takes some
#time and costs a lot memory.
>>> bm.isTurnOn( 300000000000 )
True
```

Maybe you have found that Bitmap sucks on *turnXXX* and *Memory Costing/Allocation*
when a given number is PRETTY LARGE.

*Then, my friend, what should we do?*


## Compound Bitmap
Compound Bitmap is introduced to address the above problem, and more complex
situations described below.

Just like bloom filter, compound bitmap has 'False-Positive' issue by default, and false-negtive if 'turnOff' been used.

#### For simple 'digit_string':
```Python
>>> from Compound_Bitmap import CompoundBitmap
>>> cbm = CompoundBitmap()
>>> cbm.turnOn( '300000000000' ) # NOTICE: '300000000000' is a str
>>> cbm.isTurnOn( '300000000000' )
True
```

*Then, how about any ascii-code, esp, human-readable string (like, each char is
an alnum)?*
#### For any 'human-readable string':
```Python
>>> cbm.turnOn( 'xiangshou24@gmail.com' )
>>> cbm.isTurnOn( 'xiangshou24@gmail.com' )
True
```

And, maybe, now, you have smelled something behind the implemetation of the compound bitmap,
hope you are right :p

## Performance

perf statistics on my poor air:
##### Bitmap
```Python
>>>%timeit bm.turnOn( 123456 )
100000 loops, best of 3: 4.86 µs per loop
>>>%timeit bm.isTurnOn( 123456 )
100000 loops, best of 3: 3.4 µs per loop
```

##### CompoundBitmap
```Python
>>>%timeit cbm.turnOff( '300000000000' )
10000 loops, best of 3: 103 µs per loop
>>>%timeit cbm.turnOn( 'xiangshou24@gmail.com' )
10000 loops, best of 3: 168 µs per loop
>>>%timeit cbm.isTurnOn( 'whateveryouwouldliketocallit' )
1000 loops, best of 3: 216 µs per loop
>>># Dude, how about this?
>>> s = 'x'*900
>>>%timeit cbm.turnOn( s )
100 loops, best of 3: 6.27 ms per loop
>>>%timeit cbm.isTurnOn( s )
100 loops, best of 3: 5.48 ms per loop
```

## Bitmap Info
```Python
>>> # normal bitmap
>>> bm.info()
{'base_item_bit_size': 64,
 'base_item_byte_size': 8,
 'base_item_type': 'l',
 'bit_length': 311488,
 'mem_size_in_kb': 38,
 'os_bit_mask': 63,
 'os_bit_shift': 6}

>>> # compound bitmap
>>> cbm.info()
{'base_item_bit_size': 64,
 'base_item_byte_size': 8,
 'base_item_type': 'l',
 'bit_length': 60288,
 'Bitmap_count': 6,
 'mem_size_in_kb': 7,
 'n_width_raw_per_Bitmap': 2,
 'os_bit_mask': 63,
 'os_bit_shift': 6}

```


## Application
*My friend, you know what it can do, don't you?*
